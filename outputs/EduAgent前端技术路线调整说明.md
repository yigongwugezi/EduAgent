# EduAgent 前端技术路线调整说明

## 1. 调整结论

第一阶段前端技术栈从原计划的 Vue 3 调整为 React + TypeScript + Vite。

这次调整只影响前端实现方式，不推翻后端 FastAPI、多智能体架构、知识库设计和大模型接入方式。

## 2. 新技术栈

| 层次 | 技术 |
| --- | --- |
| 前端框架 | React 19 |
| 开发语言 | TypeScript |
| 构建工具 | Vite |
| 路由 | React Router |
| 状态管理 | Zustand |
| HTTP 请求 | Axios |
| 样式 | Tailwind CSS |
| Markdown | React Markdown |
| 思维导图 | Mermaid |
| 图表 | ECharts |
| 图标 | lucide-react |
| 后端 | Python 3.13.x + FastAPI |

## 3. 保留不变的部分

- 后端仍然使用 FastAPI。
- Python 版本仍统一为 3.13.x。
- 多智能体架构仍然由 `AgentOrchestrator` 调度。
- `ProfileAgent`、`KnowledgeAgent`、`DiagnosisAgent`、`PlannerAgent`、`ResourceAgent`、`ReviewAgent` 保留。
- `LLMClient` 继续负责统一模型调用，支持 mock 和 DeepSeek。
- 课程知识库仍放在 `knowledge_base/courses/{course_id}/`。

## 4. 正式接口方向

底层主流程接口保留：

```text
POST /api/agents/run
```

React 前端正式使用以下产品接口：

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

后端通过 `backend/app/routers/product.py` 提供这些接口，内部仍复用多智能体结果。

## 5. 对团队分工的影响

### 前端成员

负责范围改为：

```text
frontend/
```

主要任务：

1. 维护 React 页面和组件。
2. 修复页面中文乱码和文案问题。
3. 对接产品化接口。
4. 完成聊天页、画像页、学习路径页、资源库页。
5. 补齐 loading、empty、error、streaming 状态。

### 后端成员

负责范围仍为：

```text
backend/
```

主要任务：

1. 保持 `/api/agents/run` 可用。
2. 继续完善产品接口。
3. 把内存学习事件追踪升级为 SQLite 或 JSON 持久化。
4. 逐步把 mock 智能体替换为真实逻辑。

### 组长

重点负责：

1. 确认接口契约。
2. 统一 README 和文档。
3. 管控 Git 协作规则。
4. 检查前后端是否按统一接口开发。

## 6. Git 协作要求

从现在开始：

1. 禁止 force push 到 `main`。
2. 提交前必须先 `git pull --rebase origin main`。
3. 前端成员不得删除 `backend/`、`docs/`、`knowledge_base/`、`outputs/`。
4. 技术栈和接口变更必须先同步给组长。
5. 大文件、压缩包、构建产物不要提交。

## 7. 风险说明

采用 React 的好处：

- 当前已有 React 初版页面。
- React + TypeScript 更适合拆分复杂页面。
- 页面可继续向完整 Web 产品演进。

需要修复的问题：

- 部分前端中文文案疑似编码异常。
- 远端曾出现 force push，后续必须规范 Git 操作。
- 前端接口需要和后端产品接口继续对齐。
