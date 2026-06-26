"""Cache-to-database assembler.

Reads pre-computed ``.meta.json`` + ``.vecs.bin`` intermediate files
from a cache directory and builds the final FAISS + LlamaIndex
persisted database.  No embedding model is loaded during assembly —
all vectors already exist in the cache.

Supports partial / distributed data: works with whatever cache files
are present, ignoring missing pairs gracefully.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from llama_index.core import StorageContext
from llama_index.core.schema import TextNode
from llama_index.vector_stores.faiss import FaissVectorStore

from app.rag.config import RAGConfig

logger = logging.getLogger("app.rag.assembler")


@dataclass
class AsmResult:
    """Summary returned after assembly."""

    files_loaded: int = 0
    files_skipped: int = 0
    total_chunks: int = 0
    total_vectors: int = 0
    collection: str = ""
    elapsed_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)


# ── Public API ──────────────────────────────────────────────────────────


def discover_cache_pairs(cache_dir: str | Path) -> list[tuple[Path, Path]]:
    """Find all ``(meta_path, vecs_path)`` pairs under *cache_dir*.

    A pair is valid only when **both** ``.meta.json`` and ``.vecs.bin``
    exist for the same base filename.  Missing either → skipped with a warning.
    """
    root = Path(cache_dir).resolve()
    if not root.exists():
        logger.warning("Cache directory not found: %s", root)
        return []

    pairs: list[tuple[Path, Path]] = []
    for sub in sorted(root.iterdir()):
        if not sub.is_dir():
            continue
        for meta_file in sorted(sub.glob("*.meta.json")):
            base = meta_file.name[:-len(".meta.json")]  # e.g. "wiki_00"
            vecs_file = sub / f"{base}.vecs.bin"
            if vecs_file.exists():
                pairs.append((meta_file, vecs_file))
            else:
                logger.warning(
                    "Missing .vecs.bin for %s — skipping", meta_file
                )
    return pairs


def assemble_index(
    config: RAGConfig,
    cache_dir: str | Path,
    output_dir: str | Path | None = None,
) -> AsmResult:
    """Build the final FAISS + docstore database from cached intermediates.

    Parameters:
        config: RAG configuration.
        cache_dir: Root of the intermediate file tree (mirrors source structure).
        output_dir: Where to persist the final index.  Defaults to the
                    directory derived from ``config.rag_index_path``.

    Returns:
        An :class:`AsmResult` with counts and any errors.
    """
    t0 = time.monotonic()
    result = AsmResult(collection=config.collection_name)

    # Resolve output directory
    if output_dir is None:
        from app.rag.store import _persist_dir
        output_dir = _persist_dir(config)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Discover cache pairs ───────────────────────────────────
    pairs = discover_cache_pairs(cache_dir)
    logger.info("Found %d cache file pair(s) under %s", len(pairs), cache_dir)
    if not pairs:
        result.errors.append("No cache pairs found — nothing to assemble")
        return result

    # ── 2. Load all chunks & vectors ──────────────────────────────
    all_nodes: list[TextNode] = []
    node_counter = 0

    for meta_path, vecs_path in pairs:
        try:
            meta = _load_meta(meta_path)
            vecs = _load_vecs(vecs_path, config.embedding_dim)
        except Exception as exc:
            msg = f"Failed to load {meta_path}: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            result.files_skipped += 1
            continue

        expected = meta["chunk_count"]
        actual = vecs.shape[0]
        if expected != actual:
            msg = (
                f"Mismatch in {meta_path.name}: "
                f"{expected} chunks but {actual} vectors — skipping"
            )
            logger.error(msg)
            result.errors.append(msg)
            result.files_skipped += 1
            continue

        # Create LlamaIndex TextNodes with pre-computed embeddings.
        # The embedding is stored on the node; LlamaIndex's
        # VectorStoreIndex will detect it and skip re-encoding.
        for i, chunk in enumerate(meta["chunks"]):
            node = TextNode(
                id_=f"node_{node_counter}",
                text=chunk["text"],
                metadata={
                    "wiki_id": chunk["wiki_id"],
                    "title": chunk["title"],
                    "url": chunk["url"],
                    "source_file": chunk["source_file"],
                    "chunk_index": str(chunk["chunk_index"]),
                },
                embedding=vecs[i].tolist(),
            )
            all_nodes.append(node)
            node_counter += 1

        result.files_loaded += 1

    result.total_chunks = len(all_nodes)
    result.total_vectors = len(all_nodes)

    if result.total_vectors == 0:
        result.errors.append("No vectors loaded — nothing to persist")
        return result

    logger.info(
        "Loaded %d chunks / %d vectors from %d file(s) (%d skipped)",
        result.total_chunks,
        result.total_vectors,
        result.files_loaded,
        result.files_skipped,
    )

    # ── 3. Build LlamaIndex storage & persist ─────────────────────
    _persist_index(all_nodes, config, output_dir)

    result.elapsed_seconds = round(time.monotonic() - t0, 1)
    logger.info(
        "Assembly complete: %d vectors in %.1f s",
        result.total_vectors,
        result.elapsed_seconds,
    )
    return result


# ── Internal helpers ────────────────────────────────────────────────────


def _load_meta(path: Path) -> dict[str, Any]:
    """Load and validate a ``.meta.json`` file."""
    with open(path, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("version") != 1:
        raise ValueError(f"Unsupported meta version: {meta.get('version')}")
    return meta


def _load_vecs(path: Path, dim: int) -> np.ndarray:
    """Load a ``.vecs.bin`` file as a float32 array of shape ``(N, dim)``."""
    raw = np.fromfile(path, dtype=np.float32)
    if raw.size % dim != 0:
        raise ValueError(
            f"{path.name}: size {raw.size} not divisible by dim {dim}"
        )
    return raw.reshape(-1, dim)


def _persist_index(
    nodes: list[TextNode],
    config: RAGConfig,
    output_dir: Path,
) -> None:
    """Build a LlamaIndex ``VectorStoreIndex`` and persist to *output_dir*.

    Creates a fresh FAISS ``IndexFlatIP`` and lets ``VectorStoreIndex``
    populate it from the pre-embedded nodes.  Because every node already
    carries an ``embedding``, LlamaIndex skips the encoding step.

    This ensures the index struct (``index_store.json``) is created
    correctly so that ``load_index_from_storage()`` works at query time.
    """
    from llama_index.core import VectorStoreIndex
    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.storage.index_store import SimpleIndexStore

    # Clear previous output (assembly is idempotent — overwrites cleanly)
    _clear_dir(output_dir)

    faiss_index = faiss.IndexFlatIP(config.embedding_dim)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    docstore = SimpleDocumentStore()
    index_store = SimpleIndexStore()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore,
        index_store=index_store,
        persist_dir=str(output_dir),
    )

    # Provide a MockEmbedding so LlamaIndex doesn't try to resolve
    # the global default (which usually requires an OpenAI key).
    # The mock is never actually called because all nodes carry
    # pre-computed embeddings.
    # NOTE: Settings.embed_model is a lazy property — set it before
    # any access, otherwise the default resolver (OpenAI) triggers first.
    from llama_index.core import Settings
    from llama_index.core.embeddings.mock_embed_model import MockEmbedding

    Settings.embed_model = MockEmbedding(embed_dim=config.embedding_dim)

    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
    )

    # Persist everything
    storage_context.persist(persist_dir=str(output_dir))
    logger.info("Final index persisted to: %s (index_id=%s)", output_dir, index.index_id)


def _clear_dir(path: Path) -> None:
    """Remove all files in *path* (not subdirectories)."""
    if not path.exists():
        return
    for entry in path.iterdir():
        if entry.is_file():
            try:
                entry.unlink()
            except Exception as exc:
                logger.warning("Failed to remove %s: %s", entry, exc)
