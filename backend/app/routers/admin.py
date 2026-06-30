"""Admin routes — question bank, knowledge graph, system config, user stats.
Protected by require_admin: only teacher/admin roles can access."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.db.engine import SessionLocal
from app.db.models import (
    KnowledgePointModel,
    LearnerModel,
    MessageModel,
    QuestionModel,
    SessionModel,
    SystemConfigModel,
)
from app.middleware.auth import AuthContext, require_auth

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


# ═══════════════════════════════════════════════════════════════════════════
# Auth guard
# ═══════════════════════════════════════════════════════════════════════════


def require_admin(auth: AuthContext = Depends(require_auth)) -> AuthContext:
    if auth.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="需要管理员或教师权限")
    return auth


# ═══════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════


class QuestionCreate(BaseModel):
    subject: str = ""
    knowledge_point: str = ""
    type: str = "choice"
    difficulty: str = "medium"
    content: dict = Field(default_factory=dict)
    tags: list[str] | None = None


class QuestionUpdate(BaseModel):
    subject: str | None = None
    knowledge_point: str | None = None
    type: str | None = None
    difficulty: str | None = None
    content: dict | None = None
    tags: list[str] | None = None
    status: str | None = None


class KPCreate(BaseModel):
    subject: str = ""
    name: str = ""
    description: str | None = None
    prerequisites: list[str] | None = None
    difficulty: str = "medium"
    importance: int = 5
    chapter: str | None = None
    grade_level: str | None = None


class KPUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    prerequisites: list[str] | None = None
    difficulty: str | None = None
    importance: int | None = None
    chapter: str | None = None
    grade_level: str | None = None


class ConfigUpdate(BaseModel):
    value: str
    description: str | None = None
    category: str | None = None


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _question_dict(q: QuestionModel) -> dict:
    return {
        "id": q.id,
        "subject": q.subject,
        "knowledge_point": q.knowledge_point,
        "type": q.type,
        "difficulty": q.difficulty,
        "content": q.content,
        "tags": q.tags or [],
        "status": q.status,
        "usage_count": q.usage_count,
        "avg_score": q.avg_score,
        "created_by": q.created_by,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "updated_at": q.updated_at.isoformat() if q.updated_at else None,
    }


def _kp_dict(kp: KnowledgePointModel) -> dict:
    return {
        "id": kp.id,
        "subject": kp.subject,
        "name": kp.name,
        "description": kp.description,
        "prerequisites": kp.prerequisites or [],
        "difficulty": kp.difficulty,
        "importance": kp.importance,
        "chapter": kp.chapter,
        "grade_level": kp.grade_level,
        "metadata": kp.metadata_ or {},
        "created_at": kp.created_at.isoformat() if kp.created_at else None,
        "updated_at": kp.updated_at.isoformat() if kp.updated_at else None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# QUESTION BANK
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/admin/questions")
def list_questions(
    auth: AuthContext = Depends(require_admin),
    subject: str = Query(default=""),
    knowledge_point: str = Query(default=""),
    type: str = Query(default=""),
    difficulty: str = Query(default=""),
    status: str = Query(default="published"),
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    db = SessionLocal()
    try:
        q = db.query(QuestionModel)
        if subject:
            q = q.filter(QuestionModel.subject == subject)
        if knowledge_point:
            q = q.filter(QuestionModel.knowledge_point == knowledge_point)
        if type:
            q = q.filter(QuestionModel.type == type)
        if difficulty:
            q = q.filter(QuestionModel.difficulty == difficulty)
        if status:
            q = q.filter(QuestionModel.status == status)
        if search:
            like = f"%{search}%"
            q = q.filter(QuestionModel.content.contains(search))

        total = q.count()
        rows = q.order_by(QuestionModel.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "questions": [_question_dict(r) for r in rows],
            "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": max(1, (total + page_size - 1) // page_size)},
        }
    finally:
        db.close()


@router.post("/admin/questions")
def create_question(body: QuestionCreate, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        q = QuestionModel(
            id=f"q_{uuid.uuid4().hex[:12]}",
            subject=body.subject,
            knowledge_point=body.knowledge_point,
            type=body.type,
            difficulty=body.difficulty,
            content=body.content,
            tags=body.tags or [],
            created_by=auth.learner_id,
        )
        db.add(q)
        db.commit()
        db.refresh(q)
        return {"question": _question_dict(q)}
    finally:
        db.close()


@router.get("/admin/questions/{question_id}")
def get_question(question_id: str, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        q = db.get(QuestionModel, question_id)
        if q is None:
            raise HTTPException(status_code=404, detail="题目不存在")
        return {"question": _question_dict(q)}
    finally:
        db.close()


@router.patch("/admin/questions/{question_id}")
def update_question(question_id: str, body: QuestionUpdate, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        q = db.get(QuestionModel, question_id)
        if q is None:
            raise HTTPException(status_code=404, detail="题目不存在")
        updates = body.model_dump(exclude_none=True)
        for key, value in updates.items():
            setattr(q, key, value)
        db.commit()
        db.refresh(q)
        return {"question": _question_dict(q)}
    finally:
        db.close()


@router.delete("/admin/questions/{question_id}")
def archive_question(question_id: str, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        q = db.get(QuestionModel, question_id)
        if q is None:
            raise HTTPException(status_code=404, detail="题目不存在")
        q.status = "archived"
        db.commit()
        return {"ok": True}
    finally:
        db.close()


@router.post("/admin/questions/batch")
def batch_import(body: list[QuestionCreate], auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        created = 0
        for item in body:
            q = QuestionModel(
                id=f"q_{uuid.uuid4().hex[:12]}",
                subject=item.subject,
                knowledge_point=item.knowledge_point,
                type=item.type,
                difficulty=item.difficulty,
                content=item.content,
                tags=item.tags or [],
                created_by=auth.learner_id,
            )
            db.add(q)
            created += 1
        db.commit()
        return {"ok": True, "imported": created}
    finally:
        db.close()


@router.get("/admin/questions/export")
def export_questions(
    auth: AuthContext = Depends(require_admin),
    subject: str = Query(default=""),
    status: str = Query(default="published"),
) -> dict:
    db = SessionLocal()
    try:
        q = db.query(QuestionModel).filter(QuestionModel.status == status)
        if subject:
            q = q.filter(QuestionModel.subject == subject)
        return {"questions": [_question_dict(r) for r in q.all()]}
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE GRAPH
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/admin/knowledge")
def list_knowledge_points(
    auth: AuthContext = Depends(require_admin),
    subject: str = Query(default=""),
    chapter: str = Query(default=""),
    grade_level: str = Query(default=""),
) -> dict:
    db = SessionLocal()
    try:
        q = db.query(KnowledgePointModel)
        if subject:
            q = q.filter(KnowledgePointModel.subject == subject)
        if chapter:
            q = q.filter(KnowledgePointModel.chapter == chapter)
        if grade_level:
            q = q.filter(KnowledgePointModel.grade_level == grade_level)
        rows = q.order_by(KnowledgePointModel.chapter, KnowledgePointModel.name).all()
        return {"knowledge_points": [_kp_dict(r) for r in rows]}
    finally:
        db.close()


@router.get("/admin/knowledge/graph")
def get_knowledge_graph(
    auth: AuthContext = Depends(require_admin),
    subject: str = Query(default=""),
) -> dict:
    """Return full DAG: nodes + edges for frontend visualization."""
    db = SessionLocal()
    try:
        q = db.query(KnowledgePointModel)
        if subject:
            q = q.filter(KnowledgePointModel.subject == subject)
        rows = q.all()

        node_ids = {r.id for r in rows}
        nodes = []
        edges = []
        for r in rows:
            nodes.append({"id": r.id, "name": r.name, "difficulty": r.difficulty, "importance": r.importance, "chapter": r.chapter})
            for pre in (r.prerequisites or []):
                if pre in node_ids:
                    edges.append({"source": pre, "target": r.id})

        return {"nodes": nodes, "edges": edges}
    finally:
        db.close()


@router.post("/admin/knowledge")
def create_knowledge_point(body: KPCreate, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        kp = KnowledgePointModel(
            id=f"kp_{uuid.uuid4().hex[:12]}",
            subject=body.subject,
            name=body.name,
            description=body.description,
            prerequisites=body.prerequisites or [],
            difficulty=body.difficulty,
            importance=body.importance,
            chapter=body.chapter,
            grade_level=body.grade_level,
        )
        db.add(kp)
        db.commit()
        db.refresh(kp)
        return {"knowledge_point": _kp_dict(kp)}
    finally:
        db.close()


@router.patch("/admin/knowledge/{kp_id}")
def update_knowledge_point(kp_id: str, body: KPUpdate, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        kp = db.get(KnowledgePointModel, kp_id)
        if kp is None:
            raise HTTPException(status_code=404, detail="知识点不存在")
        updates = body.model_dump(exclude_none=True)
        for key, value in updates.items():
            setattr(kp, key, value)
        db.commit()
        db.refresh(kp)
        return {"knowledge_point": _kp_dict(kp)}
    finally:
        db.close()


@router.delete("/admin/knowledge/{kp_id}")
def delete_knowledge_point(kp_id: str, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        kp = db.get(KnowledgePointModel, kp_id)
        if kp is None:
            raise HTTPException(status_code=404, detail="知识点不存在")
        # Remove references from other KPs that list this one as prerequisite
        for other in db.query(KnowledgePointModel).all():
            preqs = list(other.prerequisites or [])
            if kp_id in preqs:
                preqs.remove(kp_id)
                other.prerequisites = preqs
        db.delete(kp)
        db.commit()
        return {"ok": True}
    finally:
        db.close()


@router.post("/admin/knowledge/validate")
def validate_graph(
    auth: AuthContext = Depends(require_admin),
    subject: str = Query(default=""),
) -> dict:
    """Check DAG for cycles (topological sort)."""
    db = SessionLocal()
    try:
        q = db.query(KnowledgePointModel)
        if subject:
            q = q.filter(KnowledgePointModel.subject == subject)
        rows = q.all()

        node_ids = {r.id for r in rows}
        adj: dict[str, list[str]] = {r.id: [] for r in rows}
        in_degree: dict[str, int] = {r.id: 0 for r in rows}

        for r in rows:
            for pre in (r.prerequisites or []):
                if pre in node_ids:
                    adj[pre].append(r.id)
                    in_degree[r.id] += 1

        # Kahn's algorithm
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        sorted_nodes = []
        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        has_cycle = len(sorted_nodes) != len(rows)
        orphans = [nid for nid, deg in in_degree.items() if deg > 0] if has_cycle else []

        return {
            "valid": not has_cycle,
            "total_nodes": len(rows),
            "has_cycle": has_cycle,
            "cycle_nodes": orphans,
            "message": "DAG 结构正常" if not has_cycle else f"检测到环，涉及 {len(orphans)} 个节点",
        }
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM CONFIG
# ═══════════════════════════════════════════════════════════════════════════


def _seed_config(db) -> None:
    """Seed default config entries from settings if the table is empty."""
    existing = db.query(SystemConfigModel).count()
    if existing > 0:
        return
    from app.config import settings

    defaults = [
        ("llm_provider", settings.llm_provider, "LLM provider name", "llm"),
        ("llm_model", settings.llm_model, "LLM model identifier", "llm"),
        ("llm_temperature", str(settings.llm_temperature), "LLM sampling temperature", "llm"),
        ("agent_timeout", str(settings.agent_timeout), "Per-agent timeout seconds", "agent"),
        ("llm_retry_count", str(settings.llm_retry_count), "LLM call retry count", "agent"),
        ("rag_enabled", str(settings.rag_enabled).lower(), "Enable RAG knowledge base", "feature"),
        ("enable_mock_fallback", str(settings.enable_mock_fallback).lower(), "Use mock demo data", "feature"),
    ]
    for key, value, desc, cat in defaults:
        db.add(SystemConfigModel(key=key, value=value, description=desc, category=cat))
    db.commit()


@router.get("/admin/config")
def list_config(auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        _seed_config(db)
        rows = db.query(SystemConfigModel).order_by(SystemConfigModel.category, SystemConfigModel.key).all()
        configs = {}
        for r in rows:
            cat = r.category or "general"
            configs.setdefault(cat, []).append({
                "key": r.key, "value": r.value, "description": r.description,
                "category": cat, "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            })
        return {"configs": configs}
    finally:
        db.close()


@router.patch("/admin/config/{key}")
def update_config(key: str, body: ConfigUpdate, auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        cfg = db.get(SystemConfigModel, key)
        if cfg is None:
            # Create new config entry
            cfg = SystemConfigModel(key=key, value=body.value, description=body.description or "", category=body.category or "general", updated_by=auth.learner_id)
            db.add(cfg)
        else:
            cfg.value = body.value
            if body.description is not None:
                cfg.description = body.description
            if body.category is not None:
                cfg.category = body.category
            cfg.updated_by = auth.learner_id
        db.commit()
        db.refresh(cfg)
        return {"config": {"key": cfg.key, "value": cfg.value, "description": cfg.description, "category": cfg.category}}
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# USER STATS
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/admin/stats/overview")
def stats_overview(auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        total_learners = db.query(LearnerModel).count()
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        active_today = db.query(LearnerModel).filter(LearnerModel.updated_at >= today).count()
        total_sessions = db.query(SessionModel).count()
        total_messages = db.query(MessageModel).filter(MessageModel.role == "user").count()

        return {
            "total_learners": total_learners,
            "active_today": active_today,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
        }
    finally:
        db.close()


@router.get("/admin/stats/users")
def stats_users(
    auth: AuthContext = Depends(require_admin),
    sort_by: str = Query(default="updated_at"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    db = SessionLocal()
    try:
        q = db.query(LearnerModel)
        if sort_by == "updated_at":
            q = q.order_by(LearnerModel.updated_at.desc())
        elif sort_by == "created_at":
            q = q.order_by(LearnerModel.created_at.desc())

        total = q.count()
        rows = q.offset((page - 1) * page_size).limit(page_size).all()

        users = []
        for learner in rows:
            session_count = db.query(SessionModel).filter(SessionModel.learner_id == learner.id).count()
            msg_count = db.query(MessageModel).filter(MessageModel.session.has(learner_id=learner.id)).count()
            users.append({
                "id": learner.id,
                "nickname": learner.nickname,
                "role": learner.role,
                "grade": learner.grade,
                "session_count": session_count,
                "message_count": msg_count,
                "last_active": learner.updated_at.isoformat() if learner.updated_at else None,
            })

        return {"users": users, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": max(1, (total + page_size - 1) // page_size)}}
    finally:
        db.close()


@router.get("/admin/stats/daily")
def stats_daily(
    auth: AuthContext = Depends(require_admin),
    days: int = Query(default=30, ge=1, le=365),
) -> dict:
    db = SessionLocal()
    try:
        from sqlalchemy import func

        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date(MessageModel.created_at).label("day"),
                func.count(MessageModel.id).label("count"),
            )
            .filter(MessageModel.role == "user", MessageModel.created_at >= since)
            .group_by("day")
            .order_by("day")
            .all()
        )

        return {"trend": [{"date": str(r.day), "count": r.count} for r in rows]}
    finally:
        db.close()


@router.get("/admin/stats/subjects")
def stats_subjects(auth: AuthContext = Depends(require_admin)) -> dict:
    db = SessionLocal()
    try:
        from sqlalchemy import func

        rows = (
            db.query(SessionModel.subject_id, func.count(SessionModel.id))
            .filter(SessionModel.subject_id.isnot(None))
            .group_by(SessionModel.subject_id)
            .all()
        )
        return {"subjects": [{"subject_id": r[0] or "unknown", "count": r[1]} for r in rows]}
    finally:
        db.close()
