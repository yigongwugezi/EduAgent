"""FAISS + SimpleDocumentStore persistence abstraction.

Uses LlamaIndex's :class:`~llama_index.core.storage.StorageContext` to
persist both the FAISS vector index and a JSON document store so that
text + metadata are retrievable at query time.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import faiss
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.indices.base import BaseIndex
from llama_index.vector_stores.faiss import FaissVectorStore

from app.rag.config import RAGConfig

logger = logging.getLogger("app.rag.store")


def _persist_dir(config: RAGConfig) -> str:
    """Directory for persisted FAISS index + docstore."""
    from app.config import settings

    path = settings.rag_index_path or f"./data/faiss/{config.collection_name}.faiss"
    # Use the directory containing the .faiss file as the persist dir
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    return d


def _index_path(config: RAGConfig) -> str:
    """Full path to the FAISS index file inside the persist dir."""
    from app.config import settings

    path = settings.rag_index_path or f"./data/faiss/{config.collection_name}.faiss"
    return os.path.abspath(path)


# ── Build-time ────────────────────────────────────────────────────────


def create_storage_context(
    config: RAGConfig,
    overwrite: bool = False,
) -> StorageContext:
    """Create a fresh ``StorageContext`` with FAISS + docstore for building.

    Parameters:
        config: RAG configuration.
        overwrite: If ``True``, delete any existing persisted data first.

    Returns:
        A ``StorageContext`` ready for ``VectorStoreIndex.from_documents()``.
    """
    persist_dir = _persist_dir(config)

    if overwrite:
        _clear_persist_dir(persist_dir)

    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.storage.index_store import SimpleIndexStore

    faiss_index = faiss.IndexFlatIP(config.embedding_dim)
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    # Provide explicit empty stores so StorageContext doesn't try to
    # load non-existent files from the cleared persist_dir.
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=SimpleDocumentStore(),
        index_store=SimpleIndexStore(),
        persist_dir=persist_dir,
    )

    logger.info(
        "Created StorageContext: persist_dir=%s, dim=%d, metric=COSINE (IP)",
        persist_dir,
        config.embedding_dim,
    )
    return storage_context


# ── Query-time ────────────────────────────────────────────────────────


def load_index(config: RAGConfig, embed_model: Any) -> BaseIndex | None:
    """Load a previously-built index from disk.

    Returns ``None`` if no persisted data exists.
    """
    persist_dir = _persist_dir(config)

    if not os.path.exists(persist_dir):
        logger.warning("Persist dir not found: %s", persist_dir)
        return None

    # Check for LlamaIndex-persisted files (docstore.json is the most reliable indicator)
    docstore_file = os.path.join(persist_dir, "docstore.json")
    if not os.path.exists(docstore_file):
        logger.warning("No persisted index found in: %s", persist_dir)
        return None

    logger.info("Loading index from: %s", persist_dir)

    vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=persist_dir,
    )

    index = load_index_from_storage(
        storage_context,
        embed_model=embed_model,
    )
    return index


# ── Persistence (called after build) ──────────────────────────────────


def persist_index(storage_context: StorageContext, persist_dir: str) -> None:
    """Persist the FAISS index and docstore to disk.

    Call after ``VectorStoreIndex.from_documents()`` completes.
    """
    storage_context.persist(persist_dir=persist_dir)
    logger.info("Index persisted to: %s", persist_dir)


# ── Utility ───────────────────────────────────────────────────────────


def collection_exists(config: RAGConfig) -> bool:
    """Check whether the RAG index has been built (persisted data exists)."""
    persist_dir = _persist_dir(config)
    docstore_file = os.path.join(persist_dir, "docstore.json")
    return os.path.exists(docstore_file)


def collection_stats(config: RAGConfig) -> dict[str, Any]:
    """Return basic metadata about the persisted index.

    Returns a dict with keys ``exists``, ``num_entities``,
    ``index_dir``, and ``embedding_dim``.
    """
    persist_dir = _persist_dir(config)
    docstore_file = os.path.join(persist_dir, "docstore.json")
    result: dict[str, Any] = {
        "collection": config.collection_name,
        "exists": False,
        "index_dir": persist_dir,
        "embedding_dim": config.embedding_dim,
    }

    try:
        if os.path.exists(docstore_file):
            result["exists"] = True
            # Load FAISS from persisted JSON to count entities
            vector_store = FaissVectorStore.from_persist_dir(persist_dir)
            result["num_entities"] = vector_store._faiss_index.ntotal
    except Exception as exc:
        logger.warning("Failed to read index stats: %s", exc)

    return result


def _clear_persist_dir(persist_dir: str) -> None:
    """Remove all persisted data in the persist dir."""
    if not os.path.exists(persist_dir):
        return
    for fname in os.listdir(persist_dir):
        fpath = os.path.join(persist_dir, fname)
        try:
            if os.path.isfile(fpath):
                os.remove(fpath)
        except Exception as exc:
            logger.warning("Failed to remove %s: %s", fpath, exc)
    logger.info("Cleared persist dir: %s", persist_dir)
