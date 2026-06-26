# RAG Knowledge Base System

> **版本**: v1.0.0 | **日期**: 2026-06-26

## 概述

RAG（Retrieval-Augmented Generation）知识库是 EduAgent 的本地语义检索引擎。
它将中文维基百科留档数据（NDJSON 格式）经清洗、分块、向量化后存入 FAISS
向量索引（文件持久化），为 Agent 和前端提供基于语义相似度的知识检索能力。

## 架构

```
┌─────────────────────────────────────────────────┐
│                  构建阶段（一次性）                 │
│                                                 │
│  NDJSON 文件  →  loader  →  chunker  →          │
│  (wiki_*)        过滤空文本   中文分块            │
│                                                 │
│       embedder  →  store (FAISS)                │
│       向量化         持久化 .faiss 文件            │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│                  查询阶段（运行时）                 │
│                                                 │
│  用户查询  →  query_engine  →  FAISS 检索        │
│             向量化+语义搜索     Top-K 结果          │
│                                                 │
│  routers/rag.py  →  GET /api/rag/search         │
│                      GET /api/rag/status         │
└─────────────────────────────────────────────────┘
```

## 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| 编排框架 | LlamaIndex >= 0.12 | 统一管理分块、嵌入、索引、检索流程 |
| 嵌入模型 | `GanymedeNil/text2vec-large-chinese` | 768 维，中文优化，HuggingFace |
| 向量存储 | FAISS (IndexFlatIP) | 文件持久化 (.faiss)，无需外部服务 |
| 相似度度量 | COSINE (Inner Product) | 向量归一化后内积等价于余弦相似度 |

> **注意**: 原计划使用 Milvus Lite，但由于 `milvus-lite>=3.0` + `pymilvus>=2.6`
> 与 `llama-index-vector-stores-milvus` 的 ORM API 存在不兼容（`AllocTimestamp`
> RPC 未实现），当前使用 FAISS 作为替代方案。FAISS 提供同等的持久化文件存储
> 和 COSINE 检索能力，后续可在兼容性解决后迁移至 Milvus。

## 模块结构

```
backend/app/rag/
  __init__.py          # 模块导出
  config.py            # RAGConfig — 非敏感参数（分块大小、模型名等）
  errors.py            # RAGServiceError — 遵循 AppError 体系
  loader.py            # NDJSON 读取、空文本过滤、去重
  chunker.py           # 中文文本清洗与分块
  embedder.py          # HuggingFaceEmbedding 封装
  store.py             # FaissVectorStore 连接管理
  indexer.py           # 构建流水线编排
  query_engine.py      # 查询引擎（RagQueryEngine）

backend/scripts/
  build_rag_db.py      # 一次性构建脚本
  verify_rag_db.py     # 构建后验证脚本

backend/app/routers/
  rag.py               # GET /api/rag/search, GET /api/rag/status
```

## 数据格式

### 原始数据（NDJSON）

每行一个 JSON 对象：

```json
{"id":"13","text":"...文章正文...","title":"数学","url":"https://zh.wikipedia.org/wiki/数学"}
```

### 分块策略

- **chunk_size**: 512 tokens（约 256–512 个中文字符）
- **chunk_overlap**: 50 tokens（保持上下文连贯）
- **分隔符优先级**: `\n\n` → `\n` → 中文句读预处理（`。！？；`后插入段落分隔）
- **过滤**: 跳过 text 为空的记录（约 26%）
- **清洗**: 去除 `-{zh-cn:...;zh-tw:...}-` 维基语言变体标记

### FAISS 索引结构

| 字段 | 类型 | 说明 |
|------|------|------|
| 向量 | float32[768] | 嵌入向量 |
| 文本 | str | 分块文本（LlamaIndex Document.text） |
| 元数据 | dict | `{wiki_id, title, url, source_file, chunk_index}` |

索引文件: `backend/data/faiss/eduagent_knowledge.faiss`

## API 接口

### `GET /api/rag/search`

语义搜索。

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| q | string | 是 | — | 查询文本（1-500 字符） |
| top_k | int | 否 | 5 | 最大返回条数（1-20） |
| sessionId | string | 否 | "" | 会话上下文 |

**响应** (ProductApiResponse 信封):

```json
{
    "status": "success",
    "data": {
        "query": "反向传播",
        "results": [
            {
                "id": "node_abc123",
                "text": "反向传播算法是人工神经网络中...",
                "title": "反向传播",
                "url": "https://zh.wikipedia.org/wiki/反向传播",
                "source_file": "AA/wiki_00",
                "score": 0.8743
            }
        ],
        "total": 5
    },
    "source": "rag"
}
```

### `GET /api/rag/status`

查询 RAG 索引状态。

```json
{
    "status": "success",
    "data": {
        "collection": "eduagent_knowledge",
        "exists": true,
        "num_entities": 3154,
        "embedding_dim": 768,
        "index_file": "./data/faiss/eduagent_knowledge.faiss"
    },
    "source": "rag"
}
```

### 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| `RAG_SERVICE_ERROR` | 503 | 知识库检索服务暂不可用 |
| `RAG_COLLECTION_NOT_FOUND` | 503 | 索引文件未构建 |

## 配置

### 敏感参数（`.env`）

```env
RAG_ENABLED=true
RAG_INDEX_PATH=./data/faiss/eduagent_knowledge.faiss
HF_HOME=./data/huggingface_cache
```

### 算法参数（`backend/app/rag/config.py`）

参见 `RAGConfig` dataclass — 分块大小、嵌入模型、索引名等。

## 使用方法

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 构建 RAG 数据库（一次性）

```bash
cd backend
python scripts/build_rag_db.py
```

可选参数：
- `--data-path PATH` — 指定数据目录
- `--max-records N` — 限制记录数（快速测试）

### 3. 验证构建结果

```bash
python scripts/verify_rag_db.py
```

### 4. 启动后端查询

```bash
uvicorn app.main:app --port 8001
curl "http://localhost:8001/api/rag/search?q=神经网络"
curl "http://localhost:8001/api/rag/status"
```

## Agent 集成（计划）

```python
from app.rag.query_engine import rag_query_engine

response = rag_query_engine.search("Python 循环 for while", top_k=5)
for r in response.results:
    print(r.title, r.score, r.url)
```

## 验收标准

- [ ] 至少 1 门课程的关联数据被索引
- [ ] 数据库包含 > 1000 条向量
- [ ] `GET /api/rag/search?q=数学` 返回相关结果
- [ ] `GET /api/rag/status` 正确报告索引状态
- [ ] 未构建时的优雅降级（返回空结果，不崩溃）
