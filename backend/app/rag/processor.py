"""Per-file NDJSON processor with atomic writes and resume support.

Processes a single ``wiki_NN`` source file into a pair of intermediate
cache files (``.meta.json`` + ``.vecs.bin``) under a mirrored directory
structure.  Only writes to the cache after a file is *fully* processed
(atomic rename from ``.tmp``).  Files already present in the cache are
skipped automatically for crash-safe resume.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from app.rag.chunker import _pre_split_chinese_sentences, clean_text
from app.rag.config import RAGConfig

logger = logging.getLogger("app.rag.processor")

VERSION = 1


@dataclass
class ProcessResult:
    """Outcome of processing a single source file."""

    source_file: str = ""
    record_count: int = 0
    chunk_count: int = 0
    skipped: bool = False
    elapsed_ms: float = 0.0
    error: str | None = None


# ── Public API ──────────────────────────────────────────────────────────


def is_processed(cache_subdir: str | Path, filename: str) -> bool:
    """Check whether *filename* already has a valid ``.meta.json`` in the cache."""
    meta_path = Path(cache_subdir) / f"{filename}.meta.json"
    return meta_path.exists()


def process_file(
    source_path: Path,
    cache_subdir: str | Path,
    config: RAGConfig,
    embed_model: Any,
) -> ProcessResult:
    """Process one NDJSON source file into cache files.

    Parameters:
        source_path: Absolute path to a ``wiki_NN`` NDJSON file.
        cache_subdir: Destination directory (e.g. ``cache_dir/AA/``).
        config: RAG configuration (chunking, embedding dim, etc.).
        embed_model: A LlamaIndex (or sentence-transformers) embedding model
                     that exposes an ``embed_batch``-compatible method.

    Returns:
        A :class:`ProcessResult` with counts, timing, and any error.
    """
    t0 = time.monotonic()
    filename = source_path.name  # e.g. "wiki_00"
    result = ProcessResult(source_file=str(source_path))

    cache_dir = Path(cache_subdir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # ── Check if already processed ─────────────────────────────────
    if is_processed(cache_subdir, filename):
        logger.info("  %s — already processed, skipping", filename)
        result.skipped = True
        return result

    # ── 1. Load records ───────────────────────────────────────────
    try:
        records = _load_file(source_path)
    except Exception as exc:
        result.error = f"Failed to load {source_path}: {exc}"
        logger.error(result.error)
        return result
    result.record_count = len(records)
    if not records:
        result.skipped = True
        logger.info("  %s — no valid records, skipping", filename)
        return result

    # ── 2. Clean & chunk ──────────────────────────────────────────
    source_file_label = f"{source_path.parent.name}/{filename}"

    chunks: list[dict[str, Any]] = []
    for rec in records:
        text = clean_text(rec.get("text", ""))
        if not text:
            continue
        text = _pre_split_chinese_sentences(text)

        # Create a single-chunk Document-like structure.
        # The SentenceSplitter would normally split here, but we handle
        # that at the text level via pre-split Chinese sentences.
        chunks.append({
            "text": text,
            "wiki_id": rec.get("id", ""),
            "title": rec.get("title", ""),
            "url": rec.get("url", ""),
            "source_file": source_file_label,
            "chunk_index": 0,
        })

    result.chunk_count = len(chunks)
    if not chunks:
        result.skipped = True
        return result

    # ── 3. Generate embeddings ────────────────────────────────────
    texts = [c["text"] for c in chunks]
    try:
        embeddings = _encode_texts(embed_model, texts, config)
    except Exception as exc:
        result.error = f"Embedding failed for {filename}: {exc}"
        logger.error(result.error)
        return result

    # ── 4. Write intermediate files atomically ─────────────────────
    source_checksum = _file_md5(source_path)

    meta = {
        "version": VERSION,
        "source_file": source_file_label,
        "source_checksum": source_checksum,
        "record_count": result.record_count,
        "chunk_count": result.chunk_count,
        "embedding_dim": config.embedding_dim,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "chunks": chunks,
    }

    meta_path = cache_dir / f"{filename}.meta.json"
    vecs_path = cache_dir / f"{filename}.vecs.bin"

    try:
        _atomic_write_json(meta_path, meta)
        _atomic_write_vecs(vecs_path, embeddings)
    except Exception as exc:
        result.error = f"Failed to write cache for {filename}: {exc}"
        logger.error(result.error)
        # Clean up any partial .tmp files
        _cleanup_tmp(cache_dir, filename)
        return result

    result.elapsed_ms = round((time.monotonic() - t0) * 1000)
    logger.info(
        "  %s → %d records, %d chunks (%.1f s)",
        filename,
        result.record_count,
        result.chunk_count,
        result.elapsed_ms / 1000,
    )
    return result


# ── Internal helpers ────────────────────────────────────────────────────


def _load_file(path: Path) -> list[dict[str, Any]]:
    """Load and filter a single NDJSON file."""
    from app.rag.loader import filter_empty_text, read_ndjson

    records = read_ndjson(path)
    records = filter_empty_text(records)
    return records


def _encode_texts(embed_model: Any, texts: list[str], config: RAGConfig) -> np.ndarray:
    """Generate embeddings for a list of texts.

    Uses LlamaIndex's ``HuggingFaceEmbedding.get_text_embedding_batch()``
    which returns ``list[list[float]]``.  Result is a float32 array of
    shape ``(len(texts), embedding_dim)``.
    """
    batch_size = config.embedding_batch_size
    all_vecs: list[np.ndarray] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vecs = embed_model.get_text_embedding_batch(batch)
        all_vecs.append(np.array(vecs, dtype=np.float32))

    return np.concatenate(all_vecs, axis=0)


def _file_md5(path: Path) -> str:
    """Compute MD5 hex digest of a file (used for change detection)."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_json(final_path: Path, data: Any) -> None:
    """Write JSON data atomically via a ``.tmp`` rename."""
    tmp = final_path.with_suffix(final_path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, final_path)  # atomic on Windows & POSIX


def _atomic_write_vecs(final_path: Path, arr: np.ndarray) -> None:
    """Write a float32 numpy array as a raw binary blob via ``.tmp`` rename."""
    tmp = final_path.with_suffix(final_path.suffix + ".tmp")
    arr.astype(np.float32).tofile(tmp)
    os.replace(tmp, final_path)


def _cleanup_tmp(cache_dir: Path, filename: str) -> None:
    """Remove any lingering ``.tmp`` files for *filename*."""
    for suffix in (".meta.json.tmp", ".vecs.bin.tmp"):
        p = cache_dir / f"{filename}{suffix}"
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass
