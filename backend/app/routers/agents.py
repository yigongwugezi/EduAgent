"""Core agent orchestration and diagnostic API endpoints.

Stage 2: Uses ``agent_service`` to trigger and track agent pipeline runs.
Also provides a web-search diagnostic endpoint for testing search providers.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter

from app.config import settings
from app.schemas.agent import AgentRunRequest
from app.schemas.common import ApiResponse  # noqa: F401  # kept for re-export
from app.schemas.search import SearchRequest
from app.services import agent_service
from app.services.search_client import get_search_client, search_cache
from app.utils.errors import MissingSessionIdError, SearchServiceError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agents"])


@router.post("/agents/run")
def run_agents(payload: AgentRunRequest) -> dict[str, Any]:
    """Trigger the full multi-agent learning workflow.

    Returns the orchestrator result with per-agent step metadata,
    overall status, and generated profile / diagnosis / learning_path / resources.
    """
    session_id = payload.session_id.strip()
    if not session_id:
        raise MissingSessionIdError()
    course_id = payload.course_id

    try:
        result = agent_service.run_agents(
            session_id=session_id,
            user_message=payload.user_message,
            course_id=course_id,
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "reply": result.get("reply", ""),
                "session_id": result.get("session_id", session_id),
                "course_id": result.get("course_id", course_id or ""),
                "overall_status": result.get("overall_status", "completed"),
                "overall_error": result.get("overall_error"),
                "profile": result.get("profile", {}),
                "diagnosis": result.get("diagnosis", {}),
                "learning_path": result.get("learning_path", []),
                "resources": result.get("resources", []),
                "knowledge_context": result.get("knowledge_context", {}),
                "review": result.get("review", {}),
                "agent_steps": result.get("agent_steps", []),
                "course": result.get("course"),
            },
            "request_id": f"req_agents_run_{int(time.time() * 1000)}",
        }
    except Exception as exc:
        logger.error("Agent orchestrator failed for session %s: %s", session_id, exc, exc_info=exc)
        return {
            "code": -1,
            "message": "Agent orchestrator failed, please try again",
            "data": None,
            "request_id": f"req_agents_run_{int(time.time() * 1000)}",
        }


@router.post("/search")
def web_search(payload: SearchRequest) -> dict[str, Any]:
    """Execute a web search using the configured search provider.

    This is an internal diagnostic endpoint — agents use the search service
    directly via ``get_search_client()`` rather than calling this endpoint.

    Returns cached results when available (TTL controlled by
    ``SEARCH_CACHE_TTL`` in ``.env``).
    """
    try:
        client = get_search_client(settings.search_provider)

        # Check cache first
        cached = search_cache.get(payload.query, payload.max_results)
        if cached is not None:
            return {
                "code": 0,
                "message": "success (cached)",
                "data": {
                    "query": cached.query,
                    "results": [
                        {
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet,
                            "content": r.content,
                            "source": r.source,
                        }
                        for r in cached.results
                    ],
                    "total_estimated": cached.total_estimated,
                    "source": f"{cached.source}_cached",
                    "cached": True,
                },
                "request_id": f"req_search_{int(time.time() * 1000)}",
            }

        response = client.search(
            query=payload.query,
            max_results=payload.max_results,
        )
        search_cache.set(payload.query, payload.max_results, response)

        return {
            "code": 0,
            "message": "success",
            "data": {
                "query": response.query,
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "content": r.content,
                        "source": r.source,
                    }
                    for r in response.results
                ],
                "total_estimated": response.total_estimated,
                "source": response.source,
                "cached": False,
            },
            "request_id": f"req_search_{int(time.time() * 1000)}",
        }
    except ValueError as exc:
        # Unsupported provider
        raise SearchServiceError(message=str(exc), cause=exc) from exc
    except Exception as exc:
        logger.error("Search failed: %s", exc, exc_info=exc)
        raise SearchServiceError(cause=exc) from exc