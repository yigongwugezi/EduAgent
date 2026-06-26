"""Runtime query pipeline.

Provides :class:`RagQueryEngine` — the programmatic API that agents and
routers use to perform semantic search against the pre-built FAISS vector
index and document store.

The query engine is lazy-initialised: the embedding model and persisted
index are only loaded on the first call to :meth:`search`.  This keeps
startup fast and allows graceful degradation when the index hasn't been
built yet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from llama_index.core.schema import NodeWithScore

from app.rag.config import RAGConfig, rag_config
from app.rag.embedder import create_embedding_model
from app.rag.errors import RAGServiceError
from app.rag.store import collection_exists, load_index

logger = logging.getLogger("app.rag.query_engine")


@dataclass
class SearchResult:
    """A single semantic-search hit."""

    id: str
    """Node id."""

    text: str
    """Chunk text content."""

    title: str = ""
    """Wikipedia article title."""

    url: str = ""
    """Wikipedia article URL."""

    source_file: str = ""
    """Originating NDJSON file (e.g. ``AA/wiki_00``)."""

    score: float = 0.0
    """Cosine similarity score (0–1)."""


@dataclass
class SearchResponse:
    """Complete response for a semantic search."""

    query: str
    results: list[SearchResult] = field(default_factory=list)
    total: int = 0


class RagQueryEngine:
    """Semantic search over the pre-built RAG knowledge base.

    Usage::

        engine = RagQueryEngine()
        response = engine.search("反向传播算法", top_k=5)
        for r in response.results:
            print(r.title, r.score)
    """

    def __init__(self, config: RAGConfig | None = None) -> None:
        self._config = config or rag_config
        self._index = None
        self._ready: bool | None = None

    # ── Public API ──────────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> SearchResponse:
        """Run a semantic search query.

        Parameters:
            query: Natural-language query (Chinese or English).
            top_k: Max results to return (defaults to ``config.search_top_k``).

        Returns:
            A :class:`SearchResponse` with scored, metadata-enriched results.
            Returns an empty response when the RAG database has not been built.
        """
        top_k = top_k or self._config.search_top_k

        if not self._ensure_ready():
            return SearchResponse(query=query, results=[], total=0)

        try:
            retriever = self._index.as_retriever(similarity_top_k=top_k)
            nodes: list[NodeWithScore] = retriever.retrieve(query)
        except Exception as exc:
            logger.error("Retrieval failed for query '%s': %s", query, exc)
            raise RAGServiceError(cause=exc) from exc

        results = [
            SearchResult(
                id=node.node_id,
                text=node.text or "",
                title=node.metadata.get("title", ""),
                url=node.metadata.get("url", ""),
                source_file=node.metadata.get("source_file", ""),
                score=round(node.score or 0.0, 4),
            )
            for node in nodes[:top_k]
        ]

        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
        )

    def is_ready(self) -> bool:
        """Check whether the RAG index exists and is queryable."""
        return self._ensure_ready()

    # ── Internal ────────────────────────────────────────────────────

    def _ensure_ready(self) -> bool:
        """Lazy-initialise the index on first use.  Returns ``True`` if ready."""
        if self._ready:
            return True
        if self._ready is False:
            return False

        if not collection_exists(self._config):
            logger.warning(
                "RAG index not found — returning empty results. "
                "Run scripts/build_rag_db.py first."
            )
            self._ready = False
            return False

        try:
            embed_model = create_embedding_model(self._config)
            self._index = load_index(self._config, embed_model)

            if self._index is None:
                self._ready = False
                return False

            self._ready = True
            logger.info(
                "RAG query engine ready (index=%s)",
                self._config.collection_name,
            )
            return True
        except Exception as exc:
            logger.error("Failed to initialise RAG query engine: %s", exc)
            self._ready = False
            return False


# Module-level singleton — use this everywhere.
rag_query_engine = RagQueryEngine()
