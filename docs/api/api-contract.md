# EduAgent API Contract

## 1. Base URLs

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8001
```

The backend keeps two layers of APIs:

1. Core orchestration API for the multi-agent workflow.
2. Product APIs used directly by the React frontend.

## 2. Core API

### POST /api/agents/run

Purpose: run the complete multi-agent workflow.

Request:

```json
{
  "session_id": "demo_session_001",
  "course_id": "ai_intro",
  "user_message": "我是软件工程大三学生，想十天学懂神经网络，希望多给代码实验和图解。"
}
```

Response envelope:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "session_id": "demo_session_001",
    "course_id": "ai_intro",
    "user_message": "...",
    "profile": {},
    "knowledge_context": {},
    "diagnosis": {},
    "learning_path": [],
    "resources": [],
    "agent_steps": [],
    "review": {}
  },
  "request_id": "req_agents_run"
}
```

This API is the backend source of truth. Product APIs may transform its result for frontend pages.

## 3. Product APIs For React Frontend

### POST /chat/stream

Purpose: streaming chat entry. The React chat page calls this API.

Request:

```json
{
  "sessionId": "frontend_session_001",
  "message": "我是电子信息大二学生，Python基础一般，想两周入门人工智能。"
}
```

Response: Server-Sent Events.

```text
data: {"content":"正在启动多智能体协同流程...\n","done":false}

data: {"content":"## 个性化学习方案已生成\n","done":false}

data: {"done":true}
```

### POST /chat/send

Purpose: non-streaming chat fallback.

Response:

```json
{
  "sessionId": "frontend_session_001",
  "reply": {
    "id": "assistant_msg_001",
    "role": "assistant",
    "content": "## 个性化学习方案已生成...",
    "timestamp": 1781321459000
  }
}
```

### GET /profile

Purpose: get the current student profile.

Response:

```json
{
  "profile": {
    "id": "frontend_session_001",
    "nickname": "学习者",
    "createdAt": 1781235059000,
    "updatedAt": 1781321459000,
    "dimensions": [],
    "weaknesses": [],
    "preferences": {},
    "history": {}
  }
}
```

### POST /profile/build

Purpose: build or refresh the student profile from a new message.

Request:

```json
{
  "message": "我是软件工程大三学生，线性代数比较弱，想十天学懂神经网络。"
}
```

Response:

```json
{
  "profile": {}
}
```

### GET /learning-path

Purpose: get the current personalized learning path.

Response:

```json
{
  "path": {
    "id": "path_ai_intro",
    "title": "人工智能导论个性化学习路径",
    "courseName": "人工智能导论",
    "stages": [],
    "overallProgress": 18,
    "estimatedDays": 14
  }
}
```

### GET /resources

Purpose: get generated learning resources.

Response:

```json
{
  "resources": [],
  "total": 6,
  "page": 1
}
```

### POST /feedback/event

Purpose: record learning behavior events for tracking and evaluation.

Request:

```json
{
  "event": "resource_view",
  "resourceId": "res_lecture_001",
  "duration": 5,
  "metadata": {
    "page": "resources"
  }
}
```

Response:

```json
{
  "ok": true
}
```

### GET /learning-analytics

Purpose: return basic learning behavior analytics.

Response:

```json
{
  "eventCount": 1,
  "totalStudyMinutes": 5,
  "recentEvents": [],
  "summary": "已接入学习事件追踪，可用于后续动态调整画像、资源推荐和学习路径。"
}
```

## 4. Agent Workflow

Current stage-1 workflow:

```text
IntentAgent
-> route by user intent

learning_plan:
ProfileAgent
-> KnowledgeAgent
-> DiagnosisAgent
-> PlannerAgent
-> ResourceAgent
-> ReviewAgent
```

`IntentAgent` classifies the user input before the system starts a workflow. It uses a lightweight semantic-router design:

```text
high-confidence rules
-> route example similarity
-> LLM JSON classification fallback
-> low-confidence clarification
```

Supported intents:

```text
casual_chat
profile_query
learning_plan
tutoring
resource_request
progress_feedback
project_help
unsafe
unknown
```

`ProfileAgent` can call DeepSeek when `LLM_PROVIDER=deepseek`. `IntentAgent` uses rules, example-route similarity, and the same LLM client as a fallback. Other agents currently return structured stage-1 demo data and can be replaced one by one.

## 5. Development Rules

- React frontend calls Product APIs.
- Backend agents keep `/api/agents/run` stable.
- API changes must be updated here first.
- Frontend and backend should not invent new fields independently.
