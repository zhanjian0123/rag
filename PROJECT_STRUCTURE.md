# Web RAG 知识库系统 - 项目框架

## 项目概述

智能知识库系统，支持多源知识输入（网页 URL、PDF、Word 文档），提供智能切片、混合检索、查询重写与转换等高级 RAG 功能。

**版本**: 0.2.0
**创建日期**: 2026-03-13
**最后更新**: 2026-03-13

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端框架 | Next.js 14 (React + TypeScript) |
| 数据库 | SQLite (SQLAlchemy) |
| 向量数据库 | ChromaDB |
| 网页提取 | Trafilatura |
| PDF 解析 | PyMuPDF / pdfplumber |
| Word 解析 | python-docx |
| 分词/BM25 | jieba / rank-bm25 |
| LLM/Embedding | OpenAI API / DashScope API |

---

## 目录结构

```
web-rag-trae/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── config.py           # 配置管理
│   │   ├── core/               # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # 应用配置
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── logger.py       # 日志配置
│   │   ├── models/             # 数据模型层
│   │   │   ├── __init__.py
│   │   │   ├── database.py     # SQLAlchemy 模型
│   │   │   └── schemas.py      # Pydantic 请求/响应模型
│   │   ├── routers/            # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── urls.py         # URL 管理 API
│   │   │   ├── knowledge.py    # 知识库管理 API
│   │   │   ├── chat.py         # 问答 API
│   │   │   ├── search.py       # 检索 API（待实现）
│   │   │   └── documents.py    # 文档管理 API（待实现）
│   │   ├── services/           # 核心服务层
│   │   │   ├── __init__.py
│   │   │   ├── web_extractor.py # 网页内容提取
│   │   │   ├── rag.py          # RAG 服务
│   │   │   ├── bm25_index.py   # BM25 索引
│   │   │   ├── reranker.py     # 重排序服务
│   │   │   ├── parser/         # 文档解析器（待实现）
│   │   │   │   ├── __init__.py
│   │   │   │   ├── web_parser.py    # 网页解析
│   │   │   │   ├── pdf_parser.py    # PDF 解析
│   │   │   │   └── word_parser.py   # Word 解析
│   │   │   ├── chunking.py     # 切片策略（待实现）
│   │   │   ├── retrieval.py    # 混合检索（待实现）
│   │   │   └── query_rewrite.py # 查询优化（待实现）
│   │   └── utils/              # 工具函数
│   │       ├── __init__.py
│   │       └── text.py         # 文本处理工具
│   ├── requirements.txt        # Python 依赖
│   ├── .env                    # 环境变量配置
│   └── .env.example            # 环境变量示例
│
├── frontend/                   # 前端应用
│   ├── app/                    # Next.js 页面 (App Router)
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── documents/          # 文档管理页面
│   │   ├── knowledge/          # 知识库页面
│   │   └── chat/               # 问答页面
│   ├── components/             # React 组件
│   │   ├── ui/                 # 基础 UI 组件
│   │   ├── documents/          # 文档相关组件
│   │   ├── chat/               # 问答相关组件
│   │   └── search/             # 检索相关组件
│   ├── lib/                    # 工具函数
│   │   ├── api.ts              # API 客户端
│   │   └── utils.ts
│   ├── hooks/                  # 自定义 Hooks
│   ├── types/                  # TypeScript 类型定义
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── tailwind.config.js
│
├── data/                       # 数据目录（运行时生成）
│   ├── db/                     # SQLite 数据库
│   └── chroma/                 # ChromaDB 数据
│
├── .gitignore
├── README.md                   # 项目说明
└── PROJECT_STRUCTURE.md        # 项目框架（本文件）
```

---

## 模块详细说明

### 后端模块

#### 核心配置 (`app/core/`)

| 文件 | 功能 | 状态 |
|------|------|------|
| `config.py` | 应用配置管理 | ✅ 已完成 |
| `database.py` | 数据库连接 | ✅ 已完成 |
| `logger.py` | 日志配置 | ✅ 已完成 |

#### 数据模型层 (`app/models/`)

| 文件 | 类/功能 | 状态 |
|------|---------|------|
| `database.py` | SQLAlchemy 模型 | ✅ 已完成 |
| `schemas.py` | Pydantic 请求/响应模型 | ✅ 已完成 |

#### API 路由层 (`app/routers/`)

| 文件 | 功能 | 接口 | 状态 |
|------|------|------|------|
| `urls.py` | URL 管理 | `/api/urls/*` | ✅ 已完成 |
| `knowledge.py` | 知识库管理 | `/api/knowledge/*` | ✅ 已完成 |
| `chat.py` | 问答 | `/api/chat/*` | ✅ 已完成 |
| `search.py` | 混合检索 | `/api/search/*` | 📁 待实现 |
| `documents.py` | 文档管理 | `/api/documents/*` | 📁 待实现 |

#### 核心服务层 (`app/services/`)

| 文件 | 功能 | 状态 |
|------|------|------|
| `web_extractor.py` | 网页内容提取（Trafilatura） | ✅ 已完成 |
| `rag.py` | RAG 问答服务 | ✅ 已完成 |
| `bm25_index.py` | BM25 关键词索引 | ✅ 已完成 |
| `reranker.py` | 重排序服务 | ✅ 已完成 |
| `parser/web_parser.py` | 网页解析器 | 📁 待实现 |
| `parser/pdf_parser.py` | PDF 解析器 | 📁 待实现 |
| `parser/word_parser.py` | Word 解析器 | 📁 待实现 |
| `chunking.py` | 智能切片策略 | 📁 待实现 |
| `retrieval.py` | 混合检索 | 📁 待实现 |
| `query_rewrite.py` | 查询优化 | 📁 待实现 |

---

### 前端模块

#### 页面结构

| 路径 | 组件 | 功能 | 状态 |
|------|------|------|------|
| `/` | `HomePage` | 首页/仪表盘 | 📁 待实现 |
| `/documents` | `DocumentsPage` | 文档管理 | 📁 待实现 |
| `/knowledge` | `KnowledgePage` | 知识库管理 | 📁 待实现 |
| `/chat` | `ChatPage` | 问答界面 | 📁 待实现 |

---

## 核心功能流程

### 文档处理流程

```
上传文档/URL
     │
     ▼
文档解析 ──────────────────────────────────────┐
(PDF/Word/Web)                                 │
     │                                         │
     ▼                                         │
文本清洗 & 预处理                              │
     │                                         │
     ▼                                         │
切片处理                                       │
(句子/语义/Markdown)                          │
     │                                         │
     ▼                                         │
向量化 (Embedding)                             │
     │                                         │
     ▼                                         │
存入 ChromaDB ◄────────────────────────────────┘
     │
     ▼
更新文档状态
```

### 问答检索流程

```
用户提问
     │
     ▼
查询优化 ───────────────┐
(重写/扩展/分解)        │
     │                  │
     ▼                  ▼
向量检索          BM25 检索
     │                  │
     └──────┬───────────┘
            │
            ▼
       结果融合 (加权)
            │
            ▼
       重排序 (可选)
            │
            ▼
       截取 Top-K
            │
            ▼
       LLM 生成回答
            │
            ▼
       返回答案 + 来源
```

---

## 切片策略详解

### 1. 句子切片 (`sentence`)
- 按句子边界切分
- 支持多种语言句子分割
- 可配置合并句数
- **适用**: 新闻、文章、论文

### 2. 段落切片 (`paragraph`)
- 按自然段落切分
- 保留段落结构
- **适用**: 博客、报告、通用文档

### 3. 语义切片 (`semantic`)
- 使用 LLM 识别语义边界
- 主题变化处切分
- **适用**: 复杂文档、长文本

### 4. Markdown 切片 (`markdown`)
- 按标题层级切分
- 保留 Markdown 结构
- 可配置最大层级
- **适用**: 技术文档、MD 文件

### 5. 固定长度切片 (`fixed`)
- 固定字符数切分
- 支持重叠
- **适用**: 通用场景

### 6. 混合切片 (`hybrid`)
- 多种策略组合
- 根据文档类型自动选择
- **适用**: 混合文档类型

---

## 混合检索详解

### 检索方式

| 方式 | 说明 | 优势 |
|------|------|------|
| **向量检索** | 语义相似度匹配 | 理解语义，不依赖关键词 |
| **BM25** | 关键词频率匹配 | 精确匹配，可解释性强 |
| **元数据过滤** | 按时间/来源筛选 | 缩小范围，提升精度 |

### 融合策略

```python
# 加权融合示例
final_score = α * vector_score + (1-α) * bm25_score
# α 默认 0.7，可配置
```

---

## 查询优化详解

### 查询重写
```
原始问题："这个产品怎么样？"
↓
重写后："这个产品的优缺点评价如何？"
```

### 查询扩展
```
原始问题："机器学习"
↓
扩展后："机器学习 OR ML OR 深度学习 OR 神经网络"
```

### HyDE (Hypothetical Document Embeddings)
```
问题 → LLM 生成假设答案 → 向量化假设答案 → 检索相似文档
```

### 子查询分解
```
复杂问题："A 和 B 的区别是什么？"
↓
子查询 1: "A 的特点是什么？"
子查询 2: "B 的特点是什么？"
→ 合并结果
```

---

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./web_rag.db` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB 持久化目录 | `./chroma_db` |
| `LLM_PROVIDER` | LLM 提供商 | `dashscope` |
| `CHUNK_STRATEGY` | 切片策略 | `hybrid` |
| `CHUNK_SIZE` | 切片大小 | `500` |
| `CHUNK_OVERLAP` | 切片重叠 | `100` |
| `VECTOR_WEIGHT` | 向量检索权重 | `0.7` |
| `BM25_WEIGHT` | BM25 检索权重 | `0.3` |
| `ENABLE_QUERY_REWRITE` | 启用查询重写 | `true` |
| `ENABLE_HYDE` | 启用 HyDE | `false` |
| `TOP_K` | 检索返回数量 | `10` |

---

## 开发计划

### 阶段一：基础功能
- [x] 项目架构设计
- [x] 数据库模型
- [x] 基础 API 路由
- [x] 网页内容提取
- [x] 基础 RAG 问答
- [x] BM25 索引
- [x] 重排序服务
- [ ] 文档上传解析
  - [ ] PDF 解析器
  - [ ] Word 解析器
  - [ ] 网页解析器

### 阶段二：RAG 核心
- [ ] 智能切片
  - [ ] 句子切片
  - [ ] 语义切片
  - [ ] Markdown 切片
- [ ] 混合检索
  - [ ] 结果融合
  - [ ] 查询优化

### 阶段三：高级功能
- [ ] 查询重写
- [ ] 查询扩展
- [ ] HyDE
- [ ] 前端界面

### 阶段四：优化完善
- [ ] 结果重排序优化
- [ ] 多轮对话
- [ ] 用户系统
- [ ] 批量处理优化

---

## API 接口列表

### 文档管理
| 方法 | 端点 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/documents/upload` | 上传文件 | 📁 待实现 |
| POST | `/api/documents/url` | 添加 URL | 📁 待实现 |
| GET | `/api/documents` | 获取列表 | 📁 待实现 |
| GET | `/api/documents/{id}` | 获取详情 | 📁 待实现 |
| DELETE | `/api/documents/{id}` | 删除文档 | 📁 待实现 |
| GET | `/api/documents/{id}/chunks` | 查看切片 | 📁 待实现 |

### 知识库管理
| 方法 | 端点 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/collections` | 创建集合 | ✅ 已完成 |
| GET | `/api/collections` | 获取列表 | ✅ 已完成 |
| POST | `/api/collections/{id}/build` | 构建知识库 | ✅ 已完成 |
| GET | `/api/collections/{id}/stats` | 统计信息 | ✅ 已完成 |

### URL 管理
| 方法 | 端点 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/urls/add` | 添加 URL | ✅ 已完成 |
| POST | `/api/urls/add/batch` | 批量添加 | ✅ 已完成 |
| GET | `/api/urls/list` | 获取列表 | ✅ 已完成 |
| GET | `/api/urls/{id}` | 获取详情 | ✅ 已完成 |
| DELETE | `/api/urls/{id}` | 删除 URL | ✅ 已完成 |

### 检索与问答
| 方法 | 端点 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/chat` | 问答 | ✅ 已完成 |
| POST | `/api/chat/stream` | 流式问答 | 📁 待实现 |
| POST | `/api/search` | 向量检索 | 📁 待实现 |
| POST | `/api/search/hybrid` | 混合检索 | 📁 待实现 |
| POST | `/api/query/rewrite` | 查询重写 | 📁 待实现 |

---

## 依赖列表

### Python 依赖 (`requirements.txt`)

```
# 核心框架
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0

# 数据库
sqlalchemy==2.0.25
chromadb==0.4.22

# 文档解析
trafilatura==1.8.2
httpx==0.26.0
PyMuPDF>=1.23.0        # PDF 解析
python-docx>=1.1.0     # Word 解析

# 文本处理
jieba>=0.42.0          # 中文分词
rank-bm25==0.2.2       # BM25 检索
markdown>=3.5.0        # Markdown 处理

# LLM
openai==1.10.0
dashscope==1.14.1
sentence-transformers>=2.2.0
```

### Node.js 依赖 (`package.json`)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "14.1.0",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1"
  }
}
```
