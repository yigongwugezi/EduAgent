# EduAgent 后端成员当前任务说明

## 1. 当前项目路线

前端已统一调整为 React + TypeScript + Vite。

后端路线不变：

```text
Python 3.13.x + FastAPI + 多智能体调度器 + 统一 LLM Client
```

后端不需要因为前端从 Vue 改为 React 而推翻重做。后端只需要稳定提供接口。

## 2. 后端当前已有内容

已经存在：

```text
backend/app/main.py
backend/app/config.py
backend/app/routers/health.py
backend/app/routers/courses.py
backend/app/routers/agents.py
backend/app/routers/product.py
backend/app/services/orchestrator.py
backend/app/services/llm_client.py
backend/app/agents/
backend/app/mock/demo_result.json
```

核心多智能体：

```text
IntentAgent
ProfileAgent
KnowledgeAgent
DiagnosisAgent
PlannerAgent
ResourceAgent
ReviewAgent
```

## 3. 两层接口

### 3.1 核心接口

```text
POST /api/agents/run
```

作用：

运行完整多智能体流程，返回原始结构化结果。

### 3.2 React 前端产品接口

```text
POST /chat/stream
POST /chat/send
GET  /profile
POST /profile/build
GET  /learning-path
GET  /resources
POST /feedback/event
GET  /learning-analytics
```

作用：

给 React 页面直接使用。内部可以复用 `/api/agents/run` 的结果并转换字段格式。

## 4. 后端成员第一阶段任务

优先级从高到低：

1. 保证 `uvicorn app.main:app --port 8001` 能启动。
2. 保证 `/api/health` 正常。
3. 保证 `/api/agents/run` 正常。
4. 保证 React 前端接口正常：
   - `/chat/stream`
   - `/profile`
   - `/learning-path`
   - `/resources`
5. 把 `product.py` 里的内存状态逐步改成 JSON 或 SQLite 持久化。
6. 继续完善 `IntentAgent`。当前已采用轻量 Semantic Router 思路：
   - 高置信规则
   - 示例句相似度匹配
   - LLM JSON 分类兜底
   - 低置信度追问

   当前区分：
   - 闲聊
   - 画像询问
   - 学习规划
   - 智能答疑
   - 资源生成
   - 学习反馈
   - 不安全请求
7. 完善 `/feedback/event`，记录：
   - 资源浏览
   - 学习时长
   - 练习提交
   - 资源收藏
   - 学习路径节点进度
8. 完善 `/learning-analytics`，输出：
   - 总学习时长
   - 最近学习行为
   - 资源使用偏好
   - 薄弱点变化
   - 学习效果评估摘要

## 5. 不要做的事

1. 不要删除前端目录。
2. 不要改真实 `.env` 并提交。
3. 不要绕开 `LLMClient` 直接在 Agent 里写死模型调用。
4. 不要随意改变前端字段名。
5. 不要 force push `main`。

## 6. 推荐开发顺序

```text
Step 1: 跑通后端
Step 2: 跑通 /api/agents/run
Step 3: 跑通 /chat/stream
Step 4: 跑通 /profile /resources /learning-path
Step 5: 做学习事件持久化
Step 6: 做学习分析
Step 7: 再把其他 Agent 接入真实 LLM
```

## 7. 判断是否完成

打开前端：

```text
http://localhost:5173
```

输入一段学生学习情况后，应该能看到：

- 对话页有流式回复
- 画像页有学生画像
- 学习路径页有阶段和节点
- 资源库页有至少 5 类资源
- `/learning-analytics` 能看到学习事件统计
