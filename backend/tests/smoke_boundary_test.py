"""
Smoke boundary tests — 对照设计文档 §12.2 的 5 个必须验证场景。

场景 A：只表达学习意向，不自动生成
场景 B：明确要求生成 → 生成学习路径
场景 C：完整微积分画像 + 开始生成 → 5 个内容化阶段
场景 D：有上下文确认词 → 生成
场景 E：无上下文确认词 → 追问，不生成
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.conversation_agent import ConversationAgent
from app.services.conversation_state import conversation_store


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_fallback(message: str, history: list[dict[str, str]] | None = None) -> dict:
    """使用规则 fallback（无 LLM）运行 ConversationAgent。"""
    return ConversationAgent(mock_data={}, llm_client=None).run(
        {
            "user_message": message,
            "conversation_history": history or [],
            "profile_facts": {"_raw_user_message": message},
        }
    )


def run_with_history(messages: list[str]) -> list[dict]:
    """模拟多轮对话，每轮返回 ConversationAgent 的结果。"""
    results = []
    history: list[dict[str, str]] = []
    for msg in messages:
        result = ConversationAgent(mock_data={}, llm_client=None).run(
            {
                "user_message": msg,
                "conversation_history": list(history),
                "profile_facts": {"_raw_user_message": msg},
            }
        )
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": result.get("reply", "")})
        results.append(result)
    return results


# ═══════════════════════════════════════════════════════════════════
# 场景 A：只表达学习意向，不自动生成
# ═══════════════════════════════════════════════════════════════════

def test_scenario_a_learning_intent_no_auto_generation() -> None:
    """用户只表达学习意向，预期：不自动生成学习方案。"""
    messages = [
        "我是大三的",
        "我想学习数据结构",
        "我学过 C 语言",
    ]
    results = run_with_history(messages)

    for i, result in enumerate(results):
        action = result.get("action", "none")
        assert_true(
            action == "none",
            f"消息'{messages[i]}'不应该触发生成，但 action={action}"
        )
        assert_true(
            not result.get("should_run_agents"),
            f"消息'{messages[i]}'不应该运行 Agent"
        )

    # 不应有任何旧人格话术
    # 注：fallback 模式 reply 可以为空（符合 §6.2 补充2），LLM 模式下 reply 不应为空
    for result in results:
        reply = result.get("reply", "")
        for blocked in ["画像完整度", "请选择方向", "当前画像信息如下"]:
            assert_true(
                blocked not in reply,
                f"旧人格话术泄漏: '{blocked}' in '{reply[:100]}'"
            )


# ═══════════════════════════════════════════════════════════════════
# 场景 B：明确要求生成 → 生成学习路径
# ═══════════════════════════════════════════════════════════════════

def test_scenario_b_explicit_generation_request() -> None:
    """已有画像信息 + 明确要求生成，预期：触发生成。"""
    result = run_fallback(
        "开始生成学习方案",
        history=[
            {"role": "user", "content": "我是大三的，我想学习数据结构，我学过 C 语言"},
            {"role": "assistant", "content": "好的，了解了你的基础情况。数据结构对你来说很合适。"},
        ],
    )

    assert_true(
        result.get("action") == "full_workflow",
        f"明确生成请求应触发 full_workflow，但 action={result.get('action')}"
    )
    assert_true(
        result.get("should_run_full_workflow"),
        "should_run_full_workflow 应为 true"
    )
    assert_true(
        result.get("should_run_agents"),
        "should_run_agents 应为 true"
    )


# ═══════════════════════════════════════════════════════════════════
# 场景 C：完整微积分画像 + 开始生成 → 预期生成
# ═══════════════════════════════════════════════════════════════════

def test_scenario_c_complete_calculus_profile() -> None:
    """完整画像 + 生成请求，预期：触发生成。"""
    result = run_fallback(
        "开始生成学习方案",
        history=[
            {"role": "user", "content": "我想一个月学微积分"},
            {"role": "assistant", "content": "好的，微积分是重要的基础课。你之前有学过相关内容吗？"},
            {"role": "user", "content": "高中导数学过，极限没学"},
            {"role": "assistant", "content": "明白了。每天大概能花多长时间？"},
            {"role": "user", "content": "每天三小时，周末休息"},
            {"role": "assistant", "content": "了解。还有其他信息吗？比如你的专业和学习目标？"},
            {"role": "user", "content": "我是大一软件工程，目标期末高分"},
        ],
    )

    assert_true(
        result.get("action") == "full_workflow",
        f"完整画像+明确生成应触发 full_workflow，但 action={result.get('action')}"
    )


# ═══════════════════════════════════════════════════════════════════
# 场景 D：有上下文确认词 → 生成
# ═══════════════════════════════════════════════════════════════════

def test_scenario_d_contextual_confirmation() -> None:
    """系统提示可以生成 + 用户确认，预期：触发生成。"""
    history = [
        {"role": "assistant", "content": "这些信息已经可以生成初版学习方案了，要现在开始吗？"}
    ]

    for confirm_word in ["可以", "好", "就这样", "按这个来", "好的", "行"]:
        result = run_fallback(confirm_word, history=history)
        assert_true(
            result.get("action") == "full_workflow",
            f"有上下文的确认词'{confirm_word}'应触发生成，但 action={result.get('action')}"
        )
        assert_true(
            result.get("should_run_full_workflow"),
            f"确认词'{confirm_word}'应设置 should_run_full_workflow"
        )


# ═══════════════════════════════════════════════════════════════════
# 场景 E：无上下文确认词 → 追问，不生成
# ═══════════════════════════════════════════════════════════════════

def test_scenario_e_bare_confirmation_no_generation() -> None:
    """无上下文 + 用户说"可以"，预期：追问，不生成。"""
    for confirm_word in ["可以", "好", "行", "嗯嗯", "好的"]:
        result = run_fallback(confirm_word)  # 无对话历史
        assert_true(
            result.get("action") == "none",
            f"无上下文确认词'{confirm_word}'不应触发生成，但 action={result.get('action')}"
        )
        assert_true(
            result.get("needs_clarification"),
            f"无上下文确认词'{confirm_word}'应标记 needs_clarification"
        )
        assert_true(
            not result.get("should_run_agents"),
            f"无上下文确认词'{confirm_word}'不应运行 Agent"
        )


# ═══════════════════════════════════════════════════════════════════
# 额外验证：fallback reply 不能包含旧人格话术（§6.1, §6.2）
# ═══════════════════════════════════════════════════════════════════

def test_fallback_reply_is_never_user_visible() -> None:
    """Fallback 只返回结构化状态，不生成用户可见自然语言（补充2）。"""
    blocked_phrases = [
        "画像完整度", "当前画像信息尚不足", "请补充以下",
        "我已为你生成", "你的学习方案如下", "请选择方向",
        "选择方向", "unknown", "fallback_rule", "无诊断数据",
    ]

    for message in [
        "你好", "我想学习微积分", "我是大三的",
        "帮我推荐资源", "开始生成学习方案",
    ]:
        result = run_fallback(message)
        reply = result.get("reply") or ""
        for phrase in blocked_phrases:
            assert_true(
                phrase not in reply,
                f"Fallback 泄漏旧人格话术: '{phrase}' in reply for '{message}': '{reply[:100]}'"
            )


# ═══════════════════════════════════════════════════════════════════
# 额外验证：fallback 不误判明确生成请求（§6.1, §11.1）
# ═══════════════════════════════════════════════════════════════════

def test_fallback_does_not_silently_kill_generation_request() -> None:
    """Fallback 不能把明确的生成请求误判为 action=none。"""
    explicit_generation = [
        "开始生成学习方案",
        "帮我生成学习方案",
        "帮我制定学习计划",
        "给我制定学习路径",
        "按这些信息生成",
        "就按这个生成",
        "给我生成学习路径",
        "生成吧",
        "开始吧",
    ]
    for message in explicit_generation:
        result = run_fallback(message)
        assert_true(
            result.get("action") != "none",
            f"明确生成请求'{message}'被误判为 action=none"
        )
        assert_true(
            result.get("should_run_agents"),
            f"明确生成请求'{message}'应运行 Agent"
        )
