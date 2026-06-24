# r436-runtime-kit / EduAgent 需求分析文档

**文档版本：V0.4**

**文档性质：项目需求分析与功能说明**

**适用范围：需求评审、课程汇报、项目答辩与验收**

## 0. 开发与运行环境

本节依据项目仓库中的 `README.md`、`frontend/package.json`、`backend/requirements.txt`、前后端 `.env.example` 及后端数据库配置整理。

### 0.1 总体开发环境

| 项目 | 配置要求 | 说明 |
|---|---|---|
| 操作系统 | Windows 为当前主要本地开发环境 | 仓库启动示例使用 PowerShell 和 Windows 虚拟环境路径 |
| 前端运行时 | Node.js + npm | 仓库未固定 Node.js 具体版本，应使用与 Vite 8、TypeScript 6 兼容的版本 |
| 后端运行时 | Python 3.13.x | README 确认的后端 Python 版本 |
| 前端开发端口 | `5173` | Vite 默认开发地址为 `http://localhost:5173` |
| 后端服务端口 | `8001` | FastAPI/Uvicorn 地址为 `http://localhost:8001` |
| 数据存储 | SQLite + SQLAlchemy | 默认数据库文件为 `backend/data/r436_runtime.db` |
| 外部模型 | DeepSeek，可切换 mock | 默认本地示例配置为 mock，真实模型需要 API Key |

### 0.2 前端技术环境

| 技术或依赖 | 仓库配置 | 主要用途 |
|---|---|---|
| React | 19.x | 前端组件和页面运行框架 |
| TypeScript | 6.x | 类型约束和前端工程开发 |
| Vite | 8.x | 前端开发服务器与构建工具 |
| React Router | 7.x | 页面路由 |
| Zustand | 5.x | 前端状态管理 |
| Axios | 1.x | HTTP 请求 |
| Tailwind CSS | 4.x | 样式系统 |
| Mermaid | 11.x | 思维导图和关系图展示 |
| React Markdown | 10.x | Markdown 学习内容展示 |
| ECharts | 6.x | 学习分析图表 |
| KaTeX | 0.17.x | 数学公式展示 |
| lucide-react | 1.x | 图标组件 |

前端环境变量：

| 变量 | 示例值 | 作用 |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8001` | 指定后端服务地址 |

### 0.3 后端技术环境

| 技术或依赖 | 仓库版本范围 | 主要用途 |
|---|---|---|
| FastAPI | `>=0.115.0,<1.0.0` | 后端 API 框架 |
| Uvicorn | `>=0.30.0,<1.0.0` | ASGI 服务运行 |
| Pydantic | `>=2.8.0,<3.0.0` | 请求、响应和配置校验 |
| pydantic-settings | `>=2.4.0,<3.0.0` | 环境变量与应用配置 |
| HTTPX | `>=0.27.0,<1.0.0` | 外部模型 HTTP 调用 |
| SQLAlchemy | `>=2.0,<3.0` | SQLite 数据访问和持久化 |
| 自研 AgentOrchestrator | 项目内部模块 | 多 Agent 调度、步骤状态和部分失败处理 |
| 统一 LLM Client | 项目内部模块 | 支持 mock、DeepSeek，并预留其他模型扩展 |

### 0.4 后端环境变量

| 变量 | 默认或示例值 | 是否必需 | 说明 |
|---|---|---|---|
| `APP_NAME` | `eduagent-backend` | 否 | 应用名称 |
| `APP_ENV` | `development` | 否 | 运行环境 |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | 是 | 前端跨域来源 |
| `LLM_PROVIDER` | `mock` 或 `deepseek` | 是 | 选择模型提供方 |
| `LLM_MODEL` | `deepseek-chat` | 使用模型时是 | 模型名称 |
| `LLM_TEMPERATURE` | `0.2` | 否 | 模型生成温度 |
| `DEEPSEEK_API_KEY` | 空 | DeepSeek 模式是 | DeepSeek 访问密钥 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek 模式是 | DeepSeek API 地址 |
| `SPARK_APP_ID` | 空 | 预留 | 星火模型扩展配置，当前主流程未确认启用 |
| `SPARK_API_KEY` | 空 | 预留 | 星火模型扩展配置，当前主流程未确认启用 |
| `SPARK_API_SECRET` | 空 | 预留 | 星火模型扩展配置，当前主流程未确认启用 |
| `QWEN_API_KEY` | 空 | 预留 | Qwen 模型扩展配置，当前主流程未确认启用 |
| `DATABASE_URL` | `sqlite:///./data/r436_runtime.db` | 否 | 数据库连接地址，后端具有该默认值 |

真实密钥只允许存放在本地 `.env` 或安全配置中，不得提交到代码仓库。

### 0.5 本地运行步骤

**后端：**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001
```

后端健康检查地址：`http://localhost:8001/api/health`。

**前端：**

```powershell
cd frontend
npm install
npm run dev
```

前端访问地址：`http://localhost:5173`。

### 0.6 模型运行方式

| 模式 | 配置 | 适用场景 |
|---|---|---|
| 本地 mock 模式 | `LLM_PROVIDER=mock` | 无外部密钥的本地开发、基础流程验证 |
| DeepSeek 模式 | `LLM_PROVIDER=deepseek` 并配置 `DEEPSEEK_API_KEY` | 需要真实模型生成画像、路径或资源的场景 |
| 规则 fallback | Agent 在允许的失败场景中使用本地规则 | 外部模型不可用时保留基础结果，必须如实标记来源 |

## 1. 引言

### 1.1 项目定位

r436-runtime-kit / EduAgent 是面向课程学习场景的个性化学习工作流系统。系统接收学生的自然语言学习需求，形成结构化学习画像，生成学习路径和学习资源，记录学习行为，形成学习分析，诊断薄弱知识点，并对关键结果进行质量审核。

本项目不是普通聊天机器人。自然语言对话是用户入口，课程学习工作流才是系统的核心业务对象。

### 1.2 建设目标

系统应建立以下课程学习闭环：

```text
学习需求输入
→ 学习者画像
→ 学习路径规划
→ 学习资源生成
→ 学习行为记录
→ 学习效果分析
→ 薄弱点诊断
→ 结果质量审核
```

具体目标包括：

- 将学生的自然语言描述转换为结构化学习需求。
- 根据学生基础、目标、时间和偏好制定个性化学习路径。
- 为学习路径提供课程范围内、类型匹配且可使用的资源。
- 持续记录学习行为，使学习结果具有数据依据。
- 根据测验、练习、反馈和进度形成可解释的薄弱点诊断。
- 检查课程串台、资源空泛、来源不明和时间预算异常等质量问题。

### 1.3 需要解决的问题

- 学习资源分散，学生难以确定当前应使用哪些资源。
- 固定课程安排无法适应不同学生的基础、目标和可用时间。
- 学习计划、资源、练习结果和学习反馈相互分离，缺少连续闭环。
- 普通学习平台通常只展示结果，不能解释学生具体薄弱在哪里。
- 生成式内容可能出现课程章节错误、资源内容空泛或来源标记不真实。
- 多课程、多任务并行时可能出现画像、路径和行为数据串用问题。

## 2. 用户与使用场景

### 2.1 用户角色

| 用户角色 | 主要需求 | 系统支持范围 |
|---|---|---|
| 学生 | 获取个性化画像、路径、资源、学习分析和薄弱点诊断 | P0 核心用户 |
| 教师或管理者 | 查看学生学习状态、薄弱主题和推荐依据 | P0 提供基础结果，P1 增强汇总与干预能力 |
| 系统维护者 | 维护课程知识、资源规则和数据质量 | 维护课程目录、章节内容和质量约束 |

### 2.2 场景一：建立学习画像

**场景描述：**学生输入专业背景、已有基础、目标课程、可用时间和学习偏好。

**示例输入：**“我是软件工程大二学生，学过 Python，但树和图比较薄弱，希望用 48 小时复习数据结构，喜欢图解和练习题。”

**系统处理：**

1. 识别输入属于学习画像更新。
2. 提取专业背景、知识基础、学习目标、薄弱点、时间预算和资源偏好。
3. 将信息写入当前 session 的十维学习画像。
4. 区分用户明确输入、系统推断和 fallback 信息。
5. 计算现有信息是否足以生成第一版学习路径。

**预期结果：**系统形成结构化画像；信息不足时保留待补充状态，不虚构高置信度信息。

### 2.3 场景二：生成学习路径与资源

**场景描述：**学生在画像建立后请求生成完整学习方案。

**系统处理：**

1. 确认当前课程和 session。
2. 从课程知识库取得有效章节和知识点。
3. 根据学生基础、学习目标和时间预算生成阶段化路径。
4. 为不同阶段生成讲义、阅读、思维导图、测验和练习等资源。
5. 对章节归属、资源内容、资源类型、来源和时间预算执行质量审核。

**预期结果：**学生获得阶段目标、学习任务、预计时长和配套资源；48 小时时间预算应形成约 2 天的合理计划。

### 2.4 场景三：记录学习行为并形成分析

**场景描述：**学生浏览资源、完成资源、提交测验或练习，并反馈资源难度。

**系统处理：**

1. 记录资源浏览与完成行为。
2. 记录测验或练习对应的知识点、正确数、错误数、总题数或正确率。
3. 记录学习路径节点进度和资源反馈。
4. 按当前 session 汇总学习时长、事件分布、活跃资源、正确率和薄弱主题。

**预期结果：**系统形成可用于后续诊断的行为证据，且不混入其他 session 的数据。

### 2.5 场景四：基于行为证据进行诊断

**场景描述：**学生完成“二叉树遍历”测验，4 题错 3 题，然后询问“我哪里比较薄弱”。

**系统处理：**

1. 读取当前 session 的画像、路径、资源和学习分析。
2. 将带知识点和结果字段的测验作为强诊断证据。
3. 将满足字段要求的练习结果作为条件强证据。
4. 将反馈和节点进度作为辅助证据，不直接据此创造薄弱知识点。
5. 排除已经完成、不需要优先重复推荐的资源。

**预期结果：**诊断指出“二叉树遍历”为高优先级薄弱点，给出“错误 3/4”等证据、置信度、数据限制和下一步行动。

### 2.6 场景五：多学习任务隔离

**场景描述：**同一学生分别使用 session A 学习“人工智能导论”，使用 session B 学习“数据结构”。

**预期结果：**

- 两个 session 的画像、路径、资源、事件、分析和诊断相互独立。
- session A 的资源完成状态不影响 session B 的推荐。
- session A 的测验结果不进入 session B 的薄弱点统计。
- 课程编号只表示课程上下文，不能代替 sessionId。

## 3. 系统边界

### 3.1 系统范围内

- 学习意图识别与任务分流。
- 学习画像建立、补充和查询。
- 课程知识与章节匹配。
- 学习路径规划与时间预算控制。
- 学习资源生成、组织和状态记录。
- 学习行为事件记录和分析。
- 基于画像与行为证据的薄弱点诊断。
- 路径、资源、来源和内容质量审核。
- 按 session 进行数据归属和隔离。

### 3.2 系统范围外

- 学籍、排课、选课和正式成绩归档。
- 支付、直播课堂、开放社区和内容交易。
- 不受课程范围约束的通用问答服务。
- 替代教师进行正式考试评价或高风险教学决策。
- P0 阶段的复杂知识图谱推理、长期能力预测和跨课程迁移分析。

## 4. 总体业务流程

### 4.1 Agent 主链路

```text
IntentAgent
→ ProfileAgent
→ PlannerAgent
→ ResourceAgent
→ Learning Events
→ Learning Analytics
→ DiagnosisAgent
→ ReviewAgent
```

课程知识库作为基础数据支撑，为路径、资源、诊断和审核提供课程范围与章节依据。

### 4.2 核心能力分层

系统核心功能并非全部由 Agent 完成。根据功能职责，可划分为 Agent 智能处理层、学习数据层和基础支撑层。

| 能力层级 | 包含内容 | 主要职责 |
|---|---|---|
| Agent 智能处理层 | IntentAgent、ProfileAgent、PlannerAgent、ResourceAgent、DiagnosisAgent、ReviewAgent | 完成意图理解、学习画像、路径规划、资源生成、薄弱点诊断和质量审核 |
| 学习数据层 | Learning Events、Learning Analytics | 记录学生学习行为，并将行为数据整理为时长、正确率、薄弱主题和近期活动等分析结果 |
| 基础支撑层 | 课程知识库、session 数据隔离、数据持久化和接口读取 | 提供课程与章节依据，保证不同学习任务的数据独立、可保存和可查询 |

Learning Events 和 Learning Analytics 不是 Agent。它们属于学习数据服务，为 DiagnosisAgent 等智能处理模块提供真实、可追踪的学习证据。

### 4.3 闭环关系

一次方案生成并不代表学习流程结束。学生使用资源后会产生新的学习事件，Learning Analytics 根据新事件更新统计结果，DiagnosisAgent 再使用新的行为证据修正薄弱点和下一步建议。因此，系统应支持“生成方案—实际学习—形成证据—再次诊断”的循环过程。

### 4.4 用户完整使用过程与接口

系统同时提供面向用户使用过程的产品接口和面向完整 Agent 编排的工作流接口。用户使用过程如下：

| 步骤 | 用户操作 | 系统功能 | 主要接口 | 主要产生或读取的数据 |
|---|---|---|---|---|
| 1 | 创建或进入学习会话 | 建立独立学习任务上下文 | `GET /chat/sessions`、会话详情接口 | Session、历史消息 |
| 2 | 输入专业、基础、目标和时间 | 识别意图并更新学习画像 | `POST /chat/send` 或 `POST /chat/stream` | Intent、Profile |
| 3 | 查看或补充学习画像 | 读取、构建或修改画像 | `GET /profile`、`POST /profile/build`、`PATCH /profile` | Profile、readiness |
| 4 | 请求生成学习方案 | 运行画像、课程、路径、资源和审核流程 | `POST /chat/send`、`POST /chat/stream` 或 `POST /api/agents/run` | Profile、Path、Resources、Review |
| 5 | 查看学习路径 | 读取当前 session 已保存的路径 | `GET /learning-path` | LearningPath、Stage |
| 6 | 更新学习节点 | 标记节点可用、进行中或已完成 | `PATCH /learning-path/nodes/{node_id}` | node_progress、路径进度 |
| 7 | 查看或生成学习资源 | 读取资源库或按主题生成资源 | `GET /resources`、`POST /resources/generate` | Resource |
| 8 | 收藏或使用资源 | 更新资源收藏和学习状态 | `POST /resources/{resource_id}/bookmark` | bookmarked、studyStatus |
| 9 | 浏览、完成、测验或练习 | 记录真实学习行为 | `POST /feedback/event` | LearningEvent |
| 10 | 提交学习反馈 | 记录资源体验和难度反馈 | `POST /feedback` 或 `POST /feedback/event` | feedback 事件 |
| 11 | 查看学习分析 | 汇总当前 session 的学习行为 | `GET /learning-analytics` | LearningAnalytics |
| 12 | 询问薄弱点 | 调用 DiagnosisAgent 形成结构化诊断 | `POST /chat/send` 或 `POST /chat/stream` | Diagnosis |
| 13 | 再次调整学习 | 根据诊断继续当前阶段或请求新方案 | 对话接口、路径与资源接口 | 新 Path、Resources、Events |
| 14 | 重置学习任务 | 清理目标 session 的消息和关联学习数据 | `POST /chat/sessions/{session_id}/reset` | Session 及其关联数据 |

所有涉及画像、路径、资源、事件、分析和诊断的操作都必须使用同一有效 sessionId。读取型接口只读取已保存数据，不应因页面查询而隐式重新运行完整 Agent 工作流。

### 4.5 接口层次说明

| 接口层次 | 用途 | 代表接口 | 需求约束 |
|---|---|---|---|
| 对话入口 | 接收学生自然语言并按意图分流 | `/chat/send`、`/chat/stream` | 同一入口可触发不同业务功能，但必须返回明确结果 |
| 产品数据接口 | 查询或更新画像、路径、资源、事件和分析 | `/profile`、`/learning-path`、`/resources`、`/feedback/event`、`/learning-analytics` | 必须按 sessionId 隔离；读取与生成职责分离 |
| Agent 工作流接口 | 一次运行完整多 Agent 编排 | `/api/agents/run` | 返回各 Agent 结果、步骤状态和整体状态 |

接口部署时可能统一增加 `/api` 前缀。本需求文档关注接口职责、输入输出和数据归属，不以具体部署前缀作为功能差异。

## 5. 核心功能需求

### 5.1 FR-01 意图识别

| 项目 | 需求说明 |
|---|---|
| 输入 | 用户消息、当前 session 上下文 |
| 处理 | 识别画像更新、画像查询、学习计划、资源请求、薄弱点诊断、进度反馈、完整工作流等意图 |
| 输出 | 标准化 intent、置信度和后续路由信息 |
| 对应接口 | `POST /chat/send`、`POST /chat/stream` |
| 规则 | 普通聊天、日期查询和澄清不得污染画像；diagnosis 必须进入结构化诊断链路 |
| 异常处理 | 无法稳定判断意图时返回澄清提示，不错误启动高成本工作流 |

### 5.2 FR-02 学习画像

| 项目 | 需求说明 |
|---|---|
| 输入 | 用户消息、已保存画像、会话事实 |
| 处理 | 提取并更新十个固定画像维度，计算分值和置信度，保留解释、证据和来源 |
| 输出 | 十维 profile、画像完整度和规划准备状态 |
| 对应接口 | `GET /profile`、`POST /profile/build`、`PATCH /profile`，以及对话入口 |
| 规则 | 用户明确输入与系统推断必须区分；缺失维度保留待补充状态 |
| 异常处理 | LLM 不可用时允许规则提取，但 source 必须标记为 fallback |

十个画像维度包括：专业背景、知识基础、学习目标、认知风格、易错模式、编程能力、学习进度、兴趣方向、学习节奏和自我效能感。

### 5.3 FR-03 学习路径规划

| 项目 | 需求说明 |
|---|---|
| 输入 | 学习画像、课程章节、知识点、时间预算和初步诊断信息 |
| 处理 | 将学习目标拆分为有顺序的阶段，设置目标、任务、时长和资源类型 |
| 输出 | estimatedDays、stages 和阶段规划原因 |
| 对应接口 | `GET /learning-path`、`POST /learning-path/generate`、`PATCH /learning-path/nodes/{node_id}` |
| 规则 | 阶段必须属于当前课程；先修内容优先；时间区间不得反向；阶段总时长不得明显超过预算 |
| 异常处理 | 信息不足时生成低完整度草稿并说明限制，或继续请求补充信息 |

### 5.4 FR-04 学习资源

| 项目 | 需求说明 |
|---|---|
| 输入 | 当前课程、学习阶段、知识点、学生偏好和难度要求 |
| 处理 | 生成或组织 lecture、reading、mindmap、quiz、practice 等资源 |
| 输出 | 资源内容、类型、阶段关联、章节关联、知识点关联、来源和质量状态 |
| 对应接口 | `GET /resources`、`POST /resources/generate`、`POST /resources/{resource_id}/bookmark` |
| 规则 | 资源不得只有标题；quiz 必须有有效题目；practice 必须有任务或步骤；mindmap 必须有有效结构 |
| 异常处理 | 生成失败时使用规则资源，并如实标记 rule_based_fallback |

### 5.5 FR-05 学习事件

| 项目 | 需求说明 |
|---|---|
| 输入 | sessionId、事件类型、资源、时长和事件元数据 |
| 处理 | 记录 resource_view、resource_complete、quiz_result、practice_result、node_progress、feedback |
| 输出 | 带 session 归属和时间戳的标准化学习事件 |
| 对应接口 | `POST /feedback/event`、`POST /feedback`、路径节点状态更新接口 |
| 规则 | 缺失或为空的 sessionId 不得写入；课程编号不得作为 sessionId 兜底 |
| 异常处理 | 无效时长按非负值处理；缺少诊断字段的事件仍可记录，但不得被过度解释 |

### 5.6 FR-06 学习分析

| 项目 | 需求说明 |
|---|---|
| 输入 | 当前 session 的学习事件集合 |
| 处理 | 汇总事件数、学习时长、活跃资源、事件分布、测验正确率、薄弱主题和近期行为 |
| 输出 | session 级 Learning Analytics |
| 对应接口 | `GET /learning-analytics` |
| 规则 | 无有效答题数据时 quizAccuracy 允许为空；weakTopics 必须具有知识点和错误结果依据 |
| 异常处理 | 没有事件时返回空统计结构，不影响其他 Agent 执行 |

### 5.7 FR-07 薄弱点诊断

| 项目 | 需求说明 |
|---|---|
| 输入 | profile、learning_path、resources、knowledge_context 和 analytics |
| 处理 | 综合画像、课程阶段和学习行为，对薄弱主题排序并生成建议 |
| 输出 | weak_topics、reason、confidence、next_actions、limitations、evidence 和推荐阶段/资源 |
| 对应接口 | 通过 `POST /chat/send` 或 `POST /chat/stream` 触发；完整工作流结果由 `POST /api/agents/run` 返回 |
| 规则 | quiz_result 为强信号；practice_result 必须同时具备知识点和结果字段；feedback 与 node_progress 只作辅助证据 |
| 异常处理 | analytics 缺失或异常时安全回退到画像和路径，并明确诊断限制 |

### 5.8 FR-08 质量审核

| 项目 | 需求说明 |
|---|---|
| 输入 | profile、knowledge_context、learning_path、resources、diagnosis |
| 处理 | 检查画像完整度、课程依据、路径结构、资源覆盖、章节匹配、内容质量、类型匹配、来源可信和时间预算 |
| 输出 | quality_status、checks、summary、anti_hallucination |
| 对应接口 | 无独立产品触发接口；包含在 `POST /api/agents/run` 和完整方案生成结果中 |
| 状态 | passed、warning、blocked |
| 规则 | 总状态按最严重检查项聚合；Review 的 blocked 不等同于主流程执行失败 |

## 6. 数据需求

### 6.1 数据分类与来源

| 数据类别 | 主要内容 | 数据来源 | 主要用途 |
|---|---|---|---|
| 学习者数据 | 专业、基础、目标、偏好、时间、薄弱点 | 用户输入、系统推断 | 建立画像和规划依据 |
| 课程数据 | 课程、章节、知识点、难度、先修关系 | 课程知识库 | 限定路径和资源范围 |
| 规划数据 | 阶段、目标、任务、时长、资源类型 | PlannerAgent | 指导学习执行 |
| 资源数据 | 内容、类型、章节、知识点、来源、状态 | ResourceAgent、规则 fallback | 支撑具体学习活动 |
| 行为数据 | 浏览、完成、测验、练习、进度、反馈 | 学生实际操作 | 形成学习效果证据 |
| 分析数据 | 时长、正确率、事件分布、薄弱主题 | Learning Analytics | 支撑诊断和推荐 |
| 诊断数据 | 薄弱点、原因、置信度、证据、限制 | DiagnosisAgent | 指导下一步学习 |
| 审核数据 | 检查项、状态和质量说明 | ReviewAgent | 暴露生成结果风险 |

### 6.2 最小数据要求

生成第一版学习方案至少需要：

- 有效 sessionId。
- 目标课程或可匹配课程的描述。
- 学生当前基础。
- 学习目标。
- 可用时间或学习周期。

形成具体薄弱知识点诊断至少需要以下一种依据：

- 用户明确描述的薄弱知识点。
- 带 topic/knowledgePoint 和错误结果的 quiz_result。
- 带 topic/knowledgePoint 和 score、accuracy、correct、wrong、total 中至少一项结果字段的 practice_result。

只有浏览、时长或完成记录时，系统可以判断学习进度，但不能形成高置信度知识掌握结论。

## 7. 核心数据结构

以下结构为业务逻辑数据结构。接口展示层可以进行命名转换，但不得改变字段含义与数据归属规则。

### 7.1 Session 数据结构（学习会话与多任务隔离数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sessionId` | string | 是 | 学习数据归属唯一键，不能为空 |
| `courseId` | string | 是 | 当前课程编号，如 `data_structures` |
| `userMessage` | string | 触发时是 | 本次自然语言输入 |
| `createdAt` | timestamp | 是 | 会话创建时间 |
| `updatedAt` | timestamp | 是 | 最近更新时间 |
| `status` | string | 否 | active、completed 或 reset 等会话状态 |

### 7.2 Profile 数据结构（用户能力图与学习画像数据）

Profile 由十个固定维度组成，每个维度使用相同结构。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 固定维度键，使用 snake_case |
| `label` | string | 是 | 中文维度名称 |
| `value` | string | 是 | 当前画像内容，缺失时可为“待补充” |
| `score` | integer | 是 | 0—100 的维度量化值 |
| `confidence` | number | 是 | 0—1 的结论置信度 |
| `explanation` | string | 是 | 当前画像结论的解释 |
| `evidence` | string | 是 | 用户原话、行为数据或推断依据 |
| `source` | string | 是 | user_input、inferred、llm_generated、diagnosis、feedback 或 rule_based_fallback |

固定维度如下：

| key | 中文名称 | 主要数据内容 |
|---|---|---|
| `major_background` | 专业背景 | 专业、年级、课程经历 |
| `knowledge_base` | 知识基础 | 已掌握内容和基础水平 |
| `learning_goal` | 学习目标 | 目标课程、预期结果和时间范围 |
| `cognitive_style` | 认知风格 | 图解、文字、案例、练习等偏好 |
| `error_patterns` | 易错模式 | 已知薄弱点和常见错误 |
| `coding_ability` | 编程能力 | 编程语言和实操能力 |
| `learning_progress` | 学习进度 | 当前学习阶段与完成情况 |
| `interest_direction` | 兴趣方向 | 重点关注主题 |
| `learning_rhythm` | 学习节奏 | 每次学习时长、频率和总周期 |
| `self_efficacy` | 自我效能感 | 学习信心和对难度的主观判断 |

### 7.3 Course 与 Chapter 数据结构（课程知识库与章节目录数据）

**Course：**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `course_id` | string | 是 | 课程唯一编号 |
| `course_name` | string | 是 | 课程名称 |
| `target_students` | list[string] | 否 | 适用学生范围 |
| `difficulty` | string | 否 | 课程总体难度 |
| `description` | string | 否 | 课程简介 |
| `chapters` | list[Chapter] | 是 | 课程章节集合 |

**Chapter：**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `chapter_id` | string | 是 | 章节唯一编号 |
| `title` | string | 是 | 章节标题 |
| `difficulty` | string | 否 | 章节难度 |
| `prerequisites` | list[string] | 否 | 先修知识 |
| `file/content` | string | 否 | 章节内容来源或正文 |

### 7.4 Learning Path 数据结构（学习路径图与阶段计划数据）

**LearningPath：**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `courseId` | string | 是 | 所属课程 |
| `title` | string | 是 | 路径名称 |
| `description` | string | 否 | 路径策略说明 |
| `estimatedDays` | integer | 是 | 预计总天数，必须大于 0 |
| `stages` | list[Stage] | 是 | 有序学习阶段 |
| `overallProgress` | integer | 否 | 总体进度，范围 0—100 |
| `source` | string | 是 | 生成来源 |

**Stage：**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `stage_id` | string | 是 | 阶段唯一编号 |
| `title` | string | 是 | 阶段名称 |
| `duration` | string | 是 | 阶段时间范围 |
| `goal` | string | 是 | 阶段学习目标 |
| `tasks` | list[string] | 是 | 阶段任务列表 |
| `resource_types` | list[string] | 是 | 阶段需要的资源类型 |
| `reason` | string | 是 | 阶段安排依据 |
| `source` | string | 是 | 阶段生成来源 |
| `progress/status` | number/string | 否 | 阶段进度或状态 |

### 7.5 Resource 数据结构（学习资源库与资源详情数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `resource_id` | string | 是 | 资源唯一编号，应具备 session 范围 |
| `type` | string | 是 | lecture、reading、mindmap、quiz、practice 等 |
| `title` | string | 是 | 资源标题 |
| `description` | string | 是 | 资源用途说明 |
| `content_format` | string | 是 | text、diagram、structured、code 等 |
| `content` | string | 条件必填 | 资源正文；quiz 可主要使用 items |
| `items` | list[object] | 条件必填 | quiz 题目、选项和答案等结构化内容 |
| `related_stage_id` | string | 是 | 关联学习阶段 |
| `related_chapter` | string | 是 | 关联课程章节 |
| `related_knowledge_points` | list[string] | 是 | 关联知识点 |
| `difficulty` | string | 是 | 资源难度 |
| `source` | string | 是 | llm_generated 或 rule_based_fallback 等真实来源 |
| `quality_status` | string | 是 | passed、fallback_passed 或其他质量状态 |
| `reason` | string | 是 | 推荐或生成该资源的原因 |
| `bookmarked` | boolean | 否 | 是否收藏 |
| `studyStatus` | string | 否 | new、viewed、completed 等学习状态 |

### 7.6 Learning Event 数据结构（学习行为记录与学习时间线数据）

**通用字段：**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sessionId` | string | 是 | 事件所属学习会话 |
| `event` | string | 是 | 事件类型 |
| `resourceId` | string | 条件必填 | 涉及资源时填写 |
| `duration` | integer | 否 | 本次学习分钟数，必须为非负值 |
| `metadata` | object | 是 | 事件特有数据 |
| `timestamp` | timestamp | 是 | 事件发生时间 |

**六类事件的 metadata：**

| 事件类型 | 关键字段 | 诊断作用 |
|---|---|---|
| `resource_view` | title、page、duration | 证明资源被查看，不证明掌握 |
| `resource_complete` | title、stageId、completedAt | 过滤已完成资源，更新进度 |
| `quiz_result` | topic/knowledgePoint、correct、wrong、total、accuracy | 强诊断证据 |
| `practice_result` | topic/knowledgePoint、score、accuracy、correct、wrong、total | 字段完整时为条件强证据 |
| `node_progress` | stageId/nodeId、status、progress | 仅用于阶段进度和下一步定位 |
| `feedback` | rating、difficultyMatch、comment、可选 topic | 辅助判断资源体验和难度匹配 |

### 7.7 Learning Analytics 数据结构（学习分析看板与行为统计数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `eventCount` | integer | 是 | 当前 session 事件总数 |
| `totalStudyMinutes` | integer | 是 | 累计学习分钟数 |
| `activeResourceCount` | integer | 是 | 发生有效行为的资源数量 |
| `eventBreakdown` | map[string, integer] | 是 | 各事件类型数量 |
| `topResources` | list[object] | 是 | 高频使用资源及次数 |
| `quizAccuracy` | integer/null | 是 | 0—100 的累计正确率，无数据时为 null |
| `weakTopics` | list[WeakTopicStat] | 是 | 根据错误数据形成的薄弱主题统计 |
| `recommendations` | list[string] | 是 | 基础学习建议 |
| `recentEvents` | list[LearningEvent] | 是 | 最近学习事件 |
| `summary` | string | 否 | 分析摘要 |

**WeakTopicStat：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `topic` | string | 知识点名称 |
| `wrongCount` | integer | 错误次数 |
| `totalCount` | integer | 总作答次数 |
| `risk` | number | 错误比例或等价风险，范围 0—1 |
| `source` | list[string] | quiz、practice、feedback 等统计来源 |
| `priority` | string | high、medium 或 low |

### 7.8 Diagnosis 数据结构（薄弱点诊断与下一步建议数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `summary` | string | 是 | 诊断摘要 |
| `weak_topics` | list[WeakTopic] | 是 | 结构化薄弱主题 |
| `weak_knowledge_points` | list[object] | 是 | 兼容路径和历史快照的薄弱知识点 |
| `reason` | string | 是 | 总体诊断原因 |
| `source` | string | 是 | 当前为 rule_based_diagnosis 等真实来源 |
| `confidence` | number | 是 | 总体置信度，范围 0—1 |
| `next_actions` | list[string] | 是 | 下一步学习行动 |
| `limitations` | list[string] | 是 | 当前数据限制 |
| `evidence` | list[string] | 是 | 可直接阅读的诊断证据 |
| `recommended_stage_id` | string/null | 是 | 推荐返回或继续的阶段 |
| `recommended_resource_ids` | list[string] | 是 | 推荐资源编号 |
| `priority` | string | 是 | 当前最高诊断优先级 |

**WeakTopic：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `topic` | string | 薄弱主题名称 |
| `reason` | string | 判断理由 |
| `source` | string | profile、learning_events 等来源 |
| `confidence` | number | 该主题置信度 |
| `priority` | string | high、medium 或 low |
| `evidence` | list[string] | 支撑该主题的证据 |
| `recommended_stage_id` | string/null | 关联阶段 |
| `recommended_resource_ids` | list[string] | 关联且未完成的资源 |

### 7.9 Review 数据结构（Agent 输出质量审核数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `quality_status` | string | 是 | passed、warning 或 blocked |
| `checks` | list[ReviewCheck] | 是 | 各项检查结果 |
| `summary` | string | 是 | 审核总体说明 |
| `anti_hallucination` | object | 是 | 反幻觉策略和知识来源信息 |

**ReviewCheck：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `check_id` | string | 检查项唯一标识 |
| `name` | string | 检查项名称 |
| `status` | string | passed、warning 或 blocked |
| `message` | string | 检查结果说明 |

主要 check_id 包括：`profile_completeness`、`knowledge_grounding`、`path_structure`、`resource_coverage`、`course_chapter_alignment`、`resource_content_quality`、`resource_type_match`、`provenance_trust`、`path_time_budget` 和 `content_safety`。

### 7.10 Agent 工作流结果（完整主链路返回与运行状态数据）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `session_id` | string | 是 | 当前学习会话 |
| `course_id` | string | 是 | 当前课程 |
| `profile` | object | 是 | 学习画像 |
| `knowledge_context` | object | 是 | 课程知识依据 |
| `diagnosis` | object | 是 | 薄弱点诊断 |
| `learning_path` | list[Stage] | 是 | 学习阶段 |
| `resources` | list[Resource] | 是 | 学习资源 |
| `review` | object | 是 | 质量审核结果 |
| `agent_steps` | list[AgentStep] | 是 | 各 Agent 执行状态 |
| `overall_status` | string | 是 | completed、partial 或 failed |
| `overall_error` | string/null | 是 | 整体错误信息 |

**AgentStep：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `agent_id` | string | Agent 标识 |
| `agent_name` | string | Agent 名称 |
| `status` | string | completed、failed、timeout 或 skipped |
| `summary` | string | 步骤摘要 |
| `error` | string/null | 错误信息 |
| `duration_ms` | number | 执行耗时 |

## 8. 业务规则与项目约束

本节依据仓库中的 API Contract、SessionId 协作约定、课程知识库规范、画像 Schema 和学习行为追踪规范整理。

| 编号 | 业务规则 |
|---|---|
| BR-01 | sessionId 是画像、路径、资源、事件、分析和诊断的数据归属键 |
| BR-02 | subjectId/courseId 只表示课程上下文，不得替代 sessionId |
| BR-03 | 主业务请求缺失或传入空 sessionId 时必须拒绝，不使用默认生产会话 |
| BR-04 | 路径和资源中的章节必须能映射到当前课程知识库 |
| BR-05 | 普通读取操作不得隐式触发完整 Agent 工作流 |
| BR-06 | 只有明确的计划、资源、诊断或完整工作流意图才执行对应模块 |
| BR-07 | LLM 和规则 fallback 均可产生结果，但 source 必须真实标记 |
| BR-08 | 缺少 topic/knowledgePoint 或结果字段时，不得稳定定位具体薄弱点 |
| BR-09 | 已完成资源不得优先重复推荐；已浏览未完成资源可以进入 next_actions |
| BR-10 | node_progress 的 completed、in_progress、available 均不能直接作为薄弱证据 |
| BR-11 | Review 总状态按 blocked、warning、passed 的严重度聚合，但不阻断主流程 |
| BR-12 | 核心响应结构保持兼容，新增字段不得删除已有字段 |

## 9. 非功能需求

| 编号 | 属性 | 需求说明 |
|---|---|---|
| NFR-01 | 数据隔离 | 不同 session 的画像、路径、资源、事件、分析和诊断互不可见 |
| NFR-02 | 可解释性 | 画像、诊断、推荐和审核应保留来源、证据、原因、置信度或限制 |
| NFR-03 | 可信性 | 不虚构课程章节；来源和 fallback 状态必须真实 |
| NFR-04 | 稳定性 | analytics 异常或部分 Agent 失败时安全回退并保留其他有效结果 |
| NFR-05 | 可测试性 | 意图、时间预算、事件统计、诊断证据、审核状态和 session 隔离均可通过断言验证 |
| NFR-06 | 兼容性 | 核心接口字段和外层结构保持稳定 |
| NFR-07 | 性能 | 外部调用设置合理超时，避免单次请求无限等待 |
| NFR-08 | 数据最小化 | 仅保存完成学习闭环所需的数据，并限制按 session 读取 |

## 10. 需求优先级

### 10.1 P0 必须需求

- 关键学习意图正确分流。
- 十维学习画像及来源、证据和置信度。
- 课程与时间约束下的学习路径。
- 可用、类型匹配且来源清楚的学习资源。
- 六类学习事件及 session 隔离。
- 基础学习分析和 analytics 驱动诊断。
- 结构化诊断及 limitations。
- passed、warning、blocked 三态质量审核。

### 10.2 P1 增强需求

- Planner 和 Resource 的来源及 fallback 解释增强。
- 资源与知识点、阶段和难度的匹配增强。
- 诊断后学习路径和资源的动态调整。
- 教师可读的学习摘要和人工干预提示。
- 多课程配置、异常恢复和运行监控增强。

### 10.3 P2 扩展需求

- 长期学习掌握度模型。
- 完整课程知识图谱和跨课程迁移分析。
- 教师干预、班级分析和教学管理协作。
- 更丰富的多模态资源生成与质量评估。
- 长期自适应学习规划。

## 11. 需求验收标准

| 验收项 | 最小通过条件 |
|---|---|
| 意图识别 | 画像更新、计划、资源、诊断和完整工作流能够正确分流 |
| 学习画像 | 十个维度结构完整，明确输入与推断可区分 |
| 学习路径 | 48 小时可形成约 2 天计划，章节和时间安排无明显异常 |
| 学习资源 | 内容非空、类型匹配、章节属于当前课程、来源如实 |
| 学习事件 | 六类事件可按 session 写入和查询 |
| 学习分析 | 输出事件数、时长、事件分布、正确率、薄弱主题和近期事件 |
| quiz 诊断 | topic 存在且 wrong>0 或 accuracy<70 时，可影响 weak_topics |
| practice 诊断 | 仅在 topic 和结果字段同时存在时影响具体 weak_topics |
| 辅助证据 | feedback 和 node_progress 不直接创造新的薄弱主题 |
| 资源推荐 | 已完成资源不优先重复推荐，浏览未完成资源可进入下一步行动 |
| 数据不足 | limitations 明确说明无事件、缺 topic 或缺结果字段 |
| 质量审核 | 能识别课程串台、空内容、类型不符、来源异常和时间异常 |
| 会话隔离 | session A 的数据不能出现在 session B 的结果中 |
| 主流程稳定性 | Review blocked 不改变其他已完成模块的有效输出 |

## 12. 风险与限制

- Learning Analytics 当前属于轻量行为统计，不等同于正式教育测量模型。
- ReviewAgent 当前采用规则审核，可识别明确异常，但不能覆盖所有语义质量问题。
- 诊断质量依赖事件字段完整度；缺少知识点和答题结果时置信度有限。
- 多课程能力依赖课程知识库覆盖，未收录课程不得生成虚构章节。
- Planner 和 Resource 的生成结果同时依赖课程知识、模型能力与 fallback 规则，必须持续保持来源透明。

## 13. 结论

EduAgent 的核心需求是建立具有课程约束、会话隔离、行为证据、可解释诊断和质量审核能力的学习工作流。系统价值不在于完成一次聊天回复，而在于让学习需求、路径、资源、实际行为和后续诊断形成连续且可验收的闭环。
