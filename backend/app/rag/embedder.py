"""Embedding model wrapper.

Provides a singleton factory for the HuggingFace
``text2vec-large-chinese`` sentence-transformers model via LlamaIndex's
:class:`~llama_index.embeddings.huggingface.HuggingFaceEmbedding`.

Device selection is automatic: CUDA GPU when available, CPU otherwise.
"""

from __future__ import annotations

import logging
import os

import torch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.rag.config import RAGConfig

logger = logging.getLogger("app.rag.embedder")

_embed_model: HuggingFaceEmbedding | None = None


def _resolve_device() -> str:
    """Auto-detect the best available torch device.

    Returns ``"cuda"`` when a CUDA-capable GPU is present, ``"cpu"`` otherwise.
    Logs the detected device and any GPU details.
    """
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_count = torch.cuda.device_count()
        logger.info(
            "CUDA GPU detected: %s (x%d) — embedding will use GPU acceleration",
            gpu_name,
            gpu_count,
        )
        return "cuda"
    else:
        logger.info("No CUDA GPU found — embedding will use CPU")
        return "cpu"


def create_embedding_model(config: RAGConfig) -> HuggingFaceEmbedding:
    """Build (or return a cached) HuggingFace embedding model instance.

    The model is downloaded from HuggingFace Hub on first call and cached
    locally (respects ``HF_HOME`` env var / ``Settings.hf_home``).

    Device selection: CUDA GPU is used automatically when available;
    falls back to CPU otherwise.  Batch size is scaled up for GPU.
    """
    global _embed_model
    if _embed_model is not None:
        return _embed_model

    # Ensure HF_HOME is set before the model loads so the cache directory
    # is predictable (important for CI / deployment).
    from app.config import settings

    if settings.hf_home and not os.environ.get("HF_HOME"):
        os.environ["HF_HOME"] = settings.hf_home
        os.makedirs(settings.hf_home, exist_ok=True)

    device = _resolve_device()

    # GPU can handle larger batches comfortably
    batch_size = config.embedding_batch_size
    if device == "cuda":
        batch_size = batch_size * 4  # 128 on GPU vs 32 on CPU

    logger.info(
        "Loading embedding model: %s (batch_size=%d, device=%s) …",
        config.embedding_model,
        batch_size,
        device,
    )

    _embed_model = HuggingFaceEmbedding(
        model_name=config.embedding_model,
        embed_batch_size=batch_size,
        device=device,
    )

    logger.info("Embedding model ready (dim=%d, device=%s)", config.embedding_dim, device)
    return _embed_model


def get_embedding_model() -> HuggingFaceEmbedding | None:
    """Return the already-loaded model, or ``None`` if not initialised."""
    return _embed_model
