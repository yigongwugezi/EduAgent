import json
from typing import Any

from app.agents.base import BaseAgent


class ProfileAgent(BaseAgent):
    agent_id = "profile_agent"
    agent_name = "Student Profile Agent"

    profile_dimensions = [
        "major_background",
        "knowledge_base",
        "learning_goal",
        "cognitive_style",
        "weak_points",
        "programming_ability",
        "learning_progress",
        "interests",
    ]

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "profile": self._build_profile(context),
            "agent_step": self.agent_step(),
        }

    def _build_profile(self, context: dict[str, Any]) -> dict[str, Any]:
        if self.llm_client is None:
            return self.mock_data["profile"]

        try:
            content = self.llm_client.chat(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是高等教育个性化学习系统中的学生画像智能体。"
                            "你的任务是从学生自然语言描述中抽取学习画像。"
                            "如果原文出现了专业、年级、基础、目标、偏好、薄弱点，必须直接提取，"
                            "不要把已经出现的信息写成未知。只返回 JSON，不要使用 markdown 代码块。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._profile_prompt(context["user_message"]),
                    },
                ],
            )
            parsed = self._load_json(content)
            return self._normalize_profile(parsed)
        except Exception:
            return self.mock_data["profile"]

    def _profile_prompt(self, user_message: str) -> str:
        dimensions = ", ".join(self.profile_dimensions)
        return (
            "学生原始描述：\n"
            f"{user_message}\n\n"
            "请返回一个 JSON 对象，顶层必须且只能包含这些 key：\n"
            f"{dimensions}\n\n"
            "每个 key 的值必须是对象，包含这些字段："
            "label, value, confidence, source, evidence。\n"
            "要求：\n"
            "1. label 用中文短标签。\n"
            "2. value 用中文概括，优先使用学生原话中的信息。\n"
            "3. confidence 是 0 到 1 的数字。\n"
            "4. source 如果来自原文，写 user_input；如果是推断，写 inferred。\n"
            "5. evidence 写对应的学生原话片段或推断依据。\n"
            "6. 不要输出解释文字，不要输出 markdown，只输出 JSON。"
        )

    def _load_json(self, content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError("LLM response does not contain a JSON object.")

        return json.loads(text[start:end])

    def _normalize_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        normalized = {}
        fallback = self.mock_data["profile"]

        for key in self.profile_dimensions:
            item = profile.get(key)
            if not isinstance(item, dict):
                normalized[key] = fallback[key]
                continue

            normalized[key] = {
                "label": item.get("label") or fallback[key]["label"],
                "value": item.get("value") or fallback[key]["value"],
                "confidence": float(item.get("confidence", fallback[key]["confidence"])),
                "source": item.get("source") or "llm",
                "evidence": item.get("evidence") or fallback[key]["evidence"],
            }

        return normalized
