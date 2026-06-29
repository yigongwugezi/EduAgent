"""
对话核心智能体 — LLM 直接理解用户意图并生成自然回复。
替代原来 IntentAgent 的规则分类 + 模板回复。
规则引擎降级为安全检查和 LLM 失败时的兜底。

v2: LLM 主动判断何时触发后端 Agent，不再依赖规则补丁。
"""

import json
import logging
import re
from typing import Any

from app.agents.base import BaseAgent, AgentError
from app.services.llm_client import LLMClientError

logger = logging.getLogger(__name__)

# ── 安全相关常量（保留规则，因为安全不能依赖LLM） ──
HIGH_RISK_KEYWORDS = {"作弊", "代考", "代写", "破解", "攻击", "违法", "绕过检测"}
EXACT_CASUAL = {
    "你好", "您好", "hi", "hello", "在吗", "谢谢", "感谢",
    "好的", "好", "明白了", "知道了", "你是谁", "介绍一下",
}


class ConversationAgent(BaseAgent):
    """对话核心 — LLM 直接理解+决策+回复"""

    agent_id = "conversation_agent"
    agent_name = "对话智能体"

    SYSTEM_PROMPT = """你是 EduAgent，一个专业又温暖的学习助手。你像一位有经验的私人教师——能听懂学生的各种表达方式，会自然对话，不会让学生觉得在和机器人聊天。

## 你的能力
- 了解学生的学习背景（专业、基础、目标、可用时间）
- 诊断学习薄弱点（分析答题记录、行为数据、学生自述）
- 制定个性化学习计划/路径（根据诊断结果和课程知识库）
- 推荐学习资源（讲义、练习题、思维导图、实操案例等）
- 解答学习困惑（概念解释、学习方法建议）

## 对话原则
1. **自然口语化**：像老师一样说话，不要说"收到指令"、"已处理"、"请选择方向"
2. **主动理解**：即使学生表达不完整，也从上下文推断意图，少问多行动
3. **精准追问**：如果确实缺少关键信息，只问最需要的1-2个问题
4. **有记忆**：理解"这个"、"那个"、"太难了"、"换一个"等指代词
5. **有温度**：展现共情——"这个地方确实容易搞混"、"别着急，我帮你梳理"
6. **不甩锅**：不要说"我无法识别"、"请重新描述"，而是主动猜测并确认
7. **简短有力**：回复控制在2-4句话，不要长篇大论
8. **主动行动**：当信息足够时，主动说"我帮你生成学习方案"，不要等学生说"开始生成"

## 好的回复示例

学生："我想学微积分"
回复："好的！微积分是理工科的核心基础课。你之前有接触过吗？比如高中导数？还是完全零基础？每天大概能花多长时间？"

学生："帮我规划一个月的微积分学习，我大一，基础一般"
回复："明白了，大一学生，一个月时间，基础一般。我现在就帮你生成学习画像、路径和资源。<action>full_workflow</action>"

学生："零基础，每天三小时"
回复（根据上文，前面已经说了要学微积分）："好的，零基础每天三小时，一个月很充足。我现在就帮你生成完整的微积分学习方案。<action>full_workflow</action>"

学生："可以的" / "好的" / "嗯嗯" / "行"
回复（根据上文，如果前面在讨论某个学习方案）："好的，我现在就帮你生成具体的学习路径和资源。<action>full_workflow</action>"

学生："太难了"
回复（根据上文）："是觉得极限的ε-δ定义不太好理解对吗？这个地方确实容易卡住。要不要我换个更直观的方式讲解？"

学生："换一个"
回复（根据上文）："好的，我给你换一道更基础的题目。试试求 x→0 时 sin(x)/x 的极限？"

## 差的回复示例（绝对禁止）
- "请选择方向：生成学习画像、规划路径、推荐资源或诊断薄弱点"
- "我无法识别你的意图，请重新描述"
- "收到，已更新学习画像。你可以继续补充薄弱点、学习时间或资源偏好"
- "根据你的需求，我将调用诊断模块进行分析"
- 光说不练——只口头描述计划但不触发 <action>full_workflow</action>

## 决策标签（极其重要！）
在回复末尾，如果需要调用后端智能体生成实际内容，用以下标签标注：
<action>full_workflow</action> — 用户要求生成完整学习方案，或者信息已经足够（有课程名+时间+基础）
<action>plan</action>        — 用户只要求规划学习路径
<action>diagnose</action>   — 用户要求诊断薄弱点
<action>resources</action>   — 用户要求推荐资源
<action>profile</action>     — 用户提供了新的画像信息需要更新
<action>none</action>        — 纯聊天、追问信息、解答问题

## 何时必须触发 <action>full_workflow</action>
满足以下条件时，必须输出 <action>full_workflow</action>，不要只口头描述：
1. 学生明确了要学的课程（如微积分、Python、数据结构）
2. 学生提供了学习时间（如一个月、每天3小时）
3. 学生表达了"开始"、"可以"、"好的"等确认意愿
4. 对话已经进行了2-3轮，信息已经足够生成方案

记住：你的任务是帮助学生真正开始学习，而不是无限聊天。当信息够了就行动！"""

    def __init__(
        self,
        mock_data: dict[str, Any] | None = None,
        llm_client: Any = None,
    ) -> None:
        super().__init__(mock_data=mock_data, llm_client=llm_client)
        self._history: list[dict[str, str]] = []

    # ── 公共接口 ──

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """主入口"""
        # 优先取原始消息（agent_service 传入），否则用加工后的（兼容旧版）
        profile_facts = context.get("profile_facts", {})
        if isinstance(profile_facts, dict) and profile_facts.get("_raw_user_message"):
            user_message = str(profile_facts["_raw_user_message"]).strip()
        else:
            user_message = str(context.get("user_message", "")).strip()

        if not user_message:
            return self._make_result(
                reply="你好！我是你的学习助手，有什么可以帮助你的？",
                action="none",
            )

        # 第1步：安全检查（保留规则）
        safety_check = self._safety_check(user_message)
        if safety_check:
            return safety_check

        # 第2步：加载对话历史
        self._load_history(context)

        # 第3步：LLM 理解 + 回复
        try:
            messages = self._build_llm_messages(user_message, context)
            raw_response = self._call_llm(messages)
            reply, action = self._parse_response(raw_response)
        except LLMClientError:
            # LLM 失败时用规则兜底
            reply, action = self._rule_fallback(user_message, context)
            logger.warning("LLM failed, using rule fallback for conversation")

        # 第4步：保存对话历史
        self._save_history(user_message, reply, context)

        return self._make_result(reply=reply, action=action)

    def load_history(self, history: list[dict[str, str]]) -> None:
        """从外部加载对话历史"""
        self._history = history

    def get_history(self) -> list[dict[str, str]]:
        """获取对话历史"""
        return list(self._history)

    # ── 安全 ──

    def _safety_check(self, message: str) -> dict[str, Any] | None:
        """安全检查。命中高风险词直接拒绝。"""
        if any(kw in message for kw in HIGH_RISK_KEYWORDS):
            return self._make_result(
                reply="抱歉，我不能协助这类请求。如果你有学习相关的问题，我很乐意帮忙。",
                action="unsafe",
            )
        return None

    # ── LLM 调用 ──

    def _build_llm_messages(self, user_message: str, context: dict) -> list[dict]:
        """构建发给 LLM 的消息"""
        msgs = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # 对话历史
        for m in self._history[-20:]:
            msgs.append(m)

        # 上下文信息
        ctx_text = self._format_context(context)
        if ctx_text:
            msgs.append({
                "role": "system",
                "content": f"当前学生状态：\n{ctx_text}"
            })

        msgs.append({"role": "user", "content": user_message})
        return msgs

    def _format_context(self, context: dict) -> str:
        """格式化上下文给 LLM"""
        parts = []

        profile = context.get("profile", {})
        if profile:
            summary = self._summarize_profile(profile)
            if summary:
                parts.append(f"【学习画像】\n{summary}")

        diagnosis = context.get("diagnosis")
        if isinstance(diagnosis, dict):
            d_parts = []
            weak = diagnosis.get("weak_knowledge_points") or diagnosis.get("weak_topics") or []
            names = []
            for w in weak:
                if isinstance(w, dict):
                    n = w.get("name") or w.get("topic") or ""
                    if n and n not in ("无诊断数据", "unknown"):
                        names.append(n)
            if names:
                d_parts.append(f"薄弱点：{'、'.join(names[:5])}")
            summary = diagnosis.get("diagnosis_summary") or diagnosis.get("summary") or ""
            if summary:
                d_parts.append(f"诊断摘要：{summary}")
            if d_parts:
                parts.append("【诊断结果】\n" + "\n".join(d_parts))

        plan = context.get("learning_path") or context.get("stages") or []
        if plan:
            titles = []
            for s in plan[:5]:
                if isinstance(s, dict) and s.get("title"):
                    titles.append(s["title"])
            if titles:
                parts.append(f"【学习路径】\n{' → '.join(titles)}")

        resources = context.get("resources") or []
        if resources:
            r_titles = []
            for r in resources[:5]:
                if isinstance(r, dict) and r.get("title"):
                    r_titles.append(r["title"])
            if r_titles:
                parts.append(f"【已有资源】\n" + "\n".join(f"· {t}" for t in r_titles))

        return "\n\n".join(parts)

    def _summarize_profile(self, profile: dict) -> str:
        """画像摘要"""
        mapping = {
            "身份/专业背景": ["major_background", "identity", "academic_background", "major"],
            "目标课程": ["interest_direction", "target_course", "learning_goal"],
            "当前基础": ["knowledge_base", "current_level"],
            "薄弱点": ["error_patterns", "weak_points"],
            "学习目标": ["learning_goal_knowledge"],
            "时间安排": ["learning_rhythm", "time_budget"],
            "学习偏好": ["cognitive_style", "learning_preference"],
        }
        lines = []
        profile_dict = self._flatten_profile(profile)
        for label, keys in mapping.items():
            for key in keys:
                val = profile_dict.get(key, "").strip()
                if val and val != "未提及":
                    lines.append(f"{label}：{val}")
                    break
        return "\n".join(lines)

    def _flatten_profile(self, profile: dict) -> dict:
        """扁平化画像"""
        flat = {}
        for key, item in profile.items():
            if isinstance(item, dict):
                val = str(item.get("value", "")).strip()
                if val:
                    flat[key] = val
            elif item:
                flat[key] = str(item)
        return flat

    def _call_llm(self, messages: list[dict]) -> str:
        """调用 LLM"""
        if not self.llm_client:
            raise LLMClientError("No LLM client configured")

        return self.llm_client.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )

    def _parse_response(self, raw: str) -> tuple[str, str]:
        """解析 LLM 回复，分离对话文本和决策标签"""
        text = raw.strip()
        action = "none"

        # 提取 action 标签
        match = re.search(r'<action>(.*?)</action>', text, re.DOTALL)
        if match:
            action = match.group(1).strip()
            # 移除标签
            text = re.sub(r'<action>.*?</action>', '', text, flags=re.DOTALL).strip()

        # 验证 action
        valid = {"diagnose", "plan", "resources", "profile", "knowledge", "full_workflow", "none", "unsafe"}
        if action not in valid:
            action = "none"

        return text, action

    # ── 规则兜底（仅在 LLM 失败时） ──

    def _rule_fallback(self, message: str, context: dict) -> tuple[str, str]:
        """LLM 失败时的规则兜底"""
        text = message.strip().lower()

        # 寒暄
        if text in EXACT_CASUAL or len(text) <= 2:
            return "你好！有什么学习上的问题需要我帮忙吗？", "none"

        # 确认性回复 → 如果历史中有课程信息，触发 full_workflow
        confirm_words = {"可以", "好的", "行", "嗯", "好", "ok", "yes", "对", "是的", "嗯嗯", "没错"}
        if text in confirm_words or any(text.startswith(w) for w in confirm_words):
            # 检查对话历史中是否有课程名
            history_text = " ".join(
                m.get("content", "") for m in context.get("conversation_history", [])
                if isinstance(m, dict)
            )
            if any(w in history_text for w in ["微积分", "数据结构", "Python", "C语言", "线性代数", "机器学习"]):
                return "好的，我现在就帮你生成完整的学习方案。", "full_workflow"

        # 学习意图
        learn_match = re.search(
            r'(?:学|学习|入门|复习|想学|要学)\s*([\u4e00-\u9fffA-Za-z+#]{2,12})',
            text
        )
        if learn_match:
            subject = learn_match.group(1)
            return f"好的，你想学{subject}。我先了解一下：你之前有基础吗？每天能花多长时间？", "none"

        # 规划意图
        if any(w in text for w in ["规划", "计划", "路径", "安排", "怎么学", "方案"]):
            return "好的，我帮你生成学习方案。先确认一下：你想学什么课程？大概有多少时间？", "full_workflow"

        # 诊断意图
        if any(w in text for w in ["薄弱", "诊断", "不会", "不懂", "哪里差"]):
            return "好的，我帮你分析一下你的薄弱点。", "diagnose"

        # 资源意图
        if any(w in text for w in ["资源", "资料", "练习", "题", "推荐"]):
            return "好的，我帮你找一些合适的学习资料。", "resources"

        # 什么都不匹配
        return "我理解你可能有些学习上的困惑。能再具体说说吗？比如想学什么、遇到了什么困难？", "none"

    # ── 对话历史 ──

    def _load_history(self, context: dict) -> None:
        """从 context 加载对话历史"""
        loaded = context.get("conversation_history")
        if isinstance(loaded, list):
            self._history = [
                m for m in loaded
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
        else:
            self._history = []

    def _save_history(self, user_msg: str, reply: str, context: dict) -> None:
        """保存对话历史"""
        self._history.append({"role": "user", "content": user_msg})
        self._history.append({"role": "assistant", "content": reply})
        # 限制长度
        if len(self._history) > 40:
            self._history = self._history[-40:]
        # 回写到 context
        context["conversation_history"] = list(self._history)

    # ── 结果构造 ──

    def _make_result(self, reply: str, action: str) -> dict[str, Any]:
        """构造返回结果"""
        return {
            "reply": reply,
            "action": action,
            "intent": self._action_to_intent(action),
            "primary_intent": self._action_to_primary_intent(action),
            "should_run_agents": action not in ("none", "unsafe"),
            "should_run_full_workflow": action == "full_workflow",
            "needs_clarification": False,
            "confidence": 0.85 if action != "none" else 0.9,
            "conversation_history": list(self._history),
            "agent_step": {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "status": "completed",
                "summary": f"对话完成，action={action}",
                "started_at": None,
                "finished_at": None,
            },
        }

    def _action_to_intent(self, action: str) -> str:
        """action 转兼容旧版 intent"""
        mapping = {
            "diagnose": "diagnosis",
            "plan": "learning_plan",
            "resources": "resource_request",
            "profile": "profile_update",
            "knowledge": "learning_plan",
            "full_workflow": "full_workflow",
            "unsafe": "unsafe",
            "none": "casual_chat",
        }
        return mapping.get(action, "unknown")

    def _action_to_primary_intent(self, action: str) -> str:
        """action 转 primary_intent"""
        mapping = {
            "diagnose": "diagnosis",
            "plan": "learning_plan",
            "resources": "resource_request",
            "profile": "profile_update",
            "knowledge": "learning_plan",
            "full_workflow": "full_workflow",
            "unsafe": "unsafe",
            "none": "general_chat",
        }
        return mapping.get(action, "unknown")