import time
from collections import Counter, defaultdict
from typing import Any


class LearningTracker:
    """In-memory learning analytics for the stage-1 demo.

    This keeps the first version lightweight while exposing a clear boundary
    for a later database implementation.
    """

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def log(self, event: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
        normalized = {
            **event,
            "sessionId": session_id or event.get("sessionId") or "frontend_session_001",
            "timestamp": event.get("timestamp") or time.time(),
        }
        self._events.append(normalized)
        return normalized

    def recent(self, session_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        events = self._filter(session_id)
        return events[-limit:]

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        events = self._filter(session_id)
        total_minutes = sum(self._duration_minutes(event) for event in events)
        resource_events = [event for event in events if event.get("resourceId")]
        resource_counter = Counter(str(event.get("resourceId")) for event in resource_events)
        event_counter = Counter(str(event.get("event", "unknown")) for event in events)

        quiz_events = [
            event
            for event in events
            if event.get("event") in {"quiz_submit", "quiz_result", "practice_result"}
        ]
        quiz_accuracy = self._quiz_accuracy(quiz_events)

        weak_topics = self._weak_topics(events)
        recommendations = self._recommendations(total_minutes, quiz_accuracy, weak_topics)

        return {
            "eventCount": len(events),
            "totalStudyMinutes": total_minutes,
            "activeResourceCount": len(resource_counter),
            "eventBreakdown": dict(event_counter),
            "topResources": [
                {"resourceId": resource_id, "count": count}
                for resource_id, count in resource_counter.most_common(5)
            ],
            "quizAccuracy": quiz_accuracy,
            "weakTopics": weak_topics,
            "recommendations": recommendations,
            "recentEvents": events[-10:],
        }

    def reset(self, session_id: str | None = None) -> None:
        if session_id is None:
            self._events.clear()
            return
        sid = session_id or "frontend_session_001"
        self._events = [event for event in self._events if event.get("sessionId") != sid]

    def _filter(self, session_id: str | None = None) -> list[dict[str, Any]]:
        if session_id is None:
            return list(self._events)
        sid = session_id or "frontend_session_001"
        return [event for event in self._events if event.get("sessionId") == sid]

    def _duration_minutes(self, event: dict[str, Any]) -> int:
        value = event.get("duration") or event.get("durationMinutes") or 0
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def _quiz_accuracy(self, events: list[dict[str, Any]]) -> int | None:
        if not events:
            return None

        correct = 0
        total = 0
        scores: list[float] = []
        for event in events:
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            if "accuracy" in metadata:
                try:
                    scores.append(float(metadata["accuracy"]))
                except (TypeError, ValueError):
                    pass
            if "score" in metadata:
                try:
                    scores.append(float(metadata["score"]))
                except (TypeError, ValueError):
                    pass
            if "correct" in metadata and "total" in metadata:
                try:
                    correct += int(metadata["correct"])
                    total += int(metadata["total"])
                except (TypeError, ValueError):
                    pass

        if total > 0:
            return round(correct / total * 100)
        if scores:
            normalized = [score * 100 if score <= 1 else score for score in scores]
            return round(sum(normalized) / len(normalized))
        return None

    def _weak_topics(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        topic_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"wrong": 0, "total": 0})
        for event in events:
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            topic = metadata.get("topic") or metadata.get("knowledgePoint")
            if not topic:
                continue
            stat = topic_stats[str(topic)]
            stat["total"] += int(metadata.get("total", 1) or 1)
            stat["wrong"] += int(metadata.get("wrong", 0) or 0)

        ranked = sorted(
            topic_stats.items(),
            key=lambda item: (item[1]["wrong"] / max(1, item[1]["total"]), item[1]["wrong"]),
            reverse=True,
        )
        return [
            {
                "topic": topic,
                "wrongCount": stat["wrong"],
                "totalCount": stat["total"],
                "risk": round(stat["wrong"] / max(1, stat["total"]), 2),
            }
            for topic, stat in ranked[:5]
            if stat["wrong"] > 0
        ]

    def _recommendations(
        self,
        total_minutes: int,
        quiz_accuracy: int | None,
        weak_topics: list[dict[str, Any]],
    ) -> list[str]:
        recommendations: list[str] = []
        if total_minutes < 30:
            recommendations.append("学习时长还偏少，建议先完成一个核心讲义和一组基础练习。")
        if quiz_accuracy is not None and quiz_accuracy < 70:
            recommendations.append("练习正确率偏低，建议降低资源难度并增加图解讲解。")
        if weak_topics:
            recommendations.append(f"优先复习薄弱知识点：{weak_topics[0]['topic']}。")
        if not recommendations:
            recommendations.append("当前学习节奏稳定，可以继续推进下一阶段任务。")
        return recommendations


learning_tracker = LearningTracker()
