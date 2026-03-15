# MechForge AI 架构文档

本文档介绍 MechForge AI 的系统架构、模块设计和数据流。

---

## 目录

- [系统概览](#系统概览)
- [模块架构](#模块架构)
- [核心模块](#核心模块)
- [数据流](#数据流)
- [技术选型](#技术选型)
- [扩展开发](#扩展开发)

---

## 系统概览

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        MechForge AI                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   CLI    │  │   GUI    │  │   Web    │  │   TUI    │        │
│  │ Terminal │  │ PyWebView│  │ FastAPI  │  │ Textual  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       └─────────────┴──────┬──────┴─────────────┘               │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐         │
│  │                   mechforge_core                    │         │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │         │
│  │  │ Config  │ │  Cache  │ │Database │ │ Logger  │  │         │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │         │
│  └─────────────────────────┬─────────────────────────┘         │
│                            │                                    │
│  ┌─────────────────────────┼─────────────────────────┐         │
│  │                         │                         │         │
│  │  ┌───────────┐  ┌───────┴───────┐  ┌───────────┐ │         │
│  │  │ mechforge │  │   mechforge   │  │ mechforge │ │         │
│  │  │    _ai    │  │   _knowledge  │  │   _work   │ │         │
│  │  │           │  │               │  │           │ │         │
│  │  │ LLM Client│  │  RAG Engine   │  │ CAE Engine│ │         │
│  │  │ MCP Tools │  │  Vector Store │  │ Mesh/Solve│ │         │
│  │  └───────────┘  └───────────────┘  └───────────┘ │         │
│  │                                                   │         │
│  └───────────────────────────────────────────────────┘         │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐         │
│  │                   External Services                 │         │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │         │
│  │  │ Ollama  │ │ OpenAI  │ │  Gmsh   │ │CalculiX │  │         │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │         │
│  └───────────────────────────────────────────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 设计原则

| 原则 | 说明 |
|------|------|
| **模块化** | 各功能模块独立，低耦合高内聚 |
| **可扩展** | 支持插件式扩展，易于添加新功能 |
| **配置驱动** | 通过配置文件控制行为，无需修改代码 |
| **异步优先** | 使用异步 I/O 提高并发性能 |

---

## 模块架构

### 模块依赖关系

```
mechforge_core (基础层)
    │
    ├── mechforge_ai (AI 对话)
    │       │
    │       └── mechforge_knowledge (知识库)
    │
    ├── mechforge_work (CAE 工作台)
    │
    ├── mechforge_web (Web 服务)
    │       │
    │       ├── mechforge_ai
    │       ├── mechforge_knowledge
    │       └── mechforge_work
    │
    └── gui_pywebview (GUI 应用)
            │
            ├── mechforge_ai
            ├── mechforge_knowledge
            ├── mechforge_work
            └── mechforge_web
```

### 模块职责

| 模块 | 职责 | 依赖 |
|------|------|------|
| `mechforge_core` | 配置、缓存、数据库、日志、安全 | 无 |
| `mechforge_ai` | AI 对话、LLM 客户端、MCP 工具 | mechforge_core |
| `mechforge_knowledge` | RAG 引擎、向量检索、文档处理 | mechforge_core |
| `mechforge_work` | CAE 工作台、网格、求解、可视化 | mechforge_core |
| `mechforge_web` | Web 服务、API、WebSocket | mechforge_core, mechforge_ai |
| `gui_pywebview` | GUI 桌面应用 | mechforge_ai, mechforge_web |
| `mechforge_theme` | UI 组件、样式 | 无 |

---

## 核心模块

### mechforge_core

核心基础模块，提供通用功能：

```
mechforge_core/
├── __init__.py
├── config.py          # Pydantic v2 配置管理
├── cache.py           # 多级缓存系统
├── database.py        # SQLite 数据库
├── logger.py          # 结构化日志
├── security.py        # 安全工具
├── exceptions.py      # 自定义异常
├── utils.py           # 工具函数
├── mcp/               # MCP 协议实现
│   ├── __init__.py
│   ├── server.py
│   ├── client.py
│   └── tools/
├── gguf_server.py     # GGUF HTTP 服务器
└── local_model_manager.py
```

**核心类**:

| 类 | 说明 |
|------|------|
| `MechForgeConfig` | 配置管理，支持 YAML/环境变量 |
| `CacheManager` | 内存 + 文件多级缓存 |
| `Database` | SQLite 数据库封装 |
| `Logger` | 结构化日志，支持 JSON 格式 |

### mechforge_ai

AI 对话模块：

```
mechforge_ai/
├── __init__.py
├── terminal.py        # 终端入口
├── llm_client.py      # LLM 客户端
├── rag_engine.py      # RAG 引擎集成
├── command_handler.py # 命令处理
├── model_cli.py       # 模型管理 CLI
└── providers/
    ├── __init__.py
    ├── base.py        # 基类
    ├── ollama.py      # Ollama 提供商
    ├── openai.py      # OpenAI 提供商
    ├── anthropic.py   # Anthropic 提供商
    └── gguf.py        # GGUF 提供商
```

**核心类**:

| 类 | 说明 |
|------|------|
| `LLMClient` | 统一 LLM 客户端接口 |
| `OllamaProvider` | Ollama 提供商实现 |
| `OpenAIProvider` | OpenAI 提供商实现 |
| `AnthropicProvider` | Anthropic 提供商实现 |
| `GGUFProvider` | GGUF 本地模型实现 |

### mechforge_knowledge

知识库模块：

```
mechforge_knowledge/
├── __init__.py
├── cli.py             # CLI 入口
├── lookup.py          # 查询引擎
├── rag.py             # RAG 实现
├── embeddings.py      # 嵌入模型
├── chunker.py         # 文档切分
└── loaders/
    ├── __init__.py
    ├── base.py
    ├── markdown.py    # Markdown 加载器
    ├── pdf.py         # PDF 加载器
    └── docx.py        # Word 加载器
```

**核心类**:

| 类 | 说明 |
|------|------|
| `RAGEngine` | RAG 检索引擎 |
| `VectorStore` | 向量数据库封装 |
| `EmbeddingModel` | 嵌入模型封装 |
| `DocumentChunker` | 文档切分器 |

### mechforge_work

CAE 工作台模块：

```
mechforge_work/
├── __init__.py
├── work_cli.py        # CLI 入口
├── cae_core.py        # CAE 核心引擎
├── mesh_engine.py     # Gmsh 网格引擎
├── solver_engine.py   # CalculiX 求解器
├── viz_engine.py      # PyVista 可视化
└── geometry/
    ├── __init__.py
    ├── loader.py      # 几何加载
    └── primitives.py  # 基本几何
```

**核心类**:

| 类 | 说明 |
|------|------|
| `CAEEngine` | CAE 核心引擎 |
| `MeshEngine` | Gmsh 网格生成 |
| `SolverEngine` | CalculiX 求解器 |
| `VizEngine` | PyVista 可视化 |

### mechforge_web

Web 服务模块：

```
mechforge_web/
├── __init__.py
├── main.py            # FastAPI 应用入口
├── api.py             # API 路由
├── middleware.py      # 安全中间件
├── security_config.py # 安全配置
├── websocket.py       # WebSocket 处理
└── templates/
    └── index.html
```

**核心类**:

| 类 | 说明 |
|------|------|
| `create_app()` | FastAPI 应用工厂 |
| `SecurityMiddleware` | 安全中间件 |
| `WebSocketHandler` | WebSocket 处理器 |

---

## 数据流

### AI 对话流程

```
用户输入
    │
    ▼
┌─────────────┐
│   CLI/GUI   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ LLM Client  │────▶│   Provider  │
└──────┬──────┘     │  (Ollama)   │
       │            └─────────────┘
       ▼
┌─────────────┐
│ RAG Engine  │ (可选)
│  检索增强   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  流式响应   │
└──────┬──────┘
       │
       ▼
   用户输出
```

### RAG 检索流程

```
用户查询
    │
    ▼
┌─────────────┐
│ Embedding   │ 查询向量化
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Vector Store│ 向量检索
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   BM25      │ 关键词检索
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Rerank    │ 重排序
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Top-K 结果 │
└─────────────┘
```

### CAE 分析流程

```
几何文件 (.step)
       │
       ▼
┌─────────────┐
│  Geometry   │ 几何加载
│   Loader    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Gmsh     │ 网格划分
│ Mesh Engine │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ CalculiX    │ FEA 求解
│   Solver    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PyVista    │ 结果可视化
│  Viz Engine │
└──────┬──────┘
       │
       ▼
   结果输出
```

---

## 技术选型

### 核心技术栈

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| **语言** | Python | 3.10+ | 生态丰富，科学计算支持好 |
| **配置** | Pydantic | 2.0+ | 类型安全，验证强大 |
| **CLI** | Typer + Rich | - | 现代化终端 UI |
| **Web** | FastAPI | 0.104+ | 高性能异步框架 |
| **数据库** | SQLite | - | 轻量级，无需部署 |
| **向量库** | ChromaDB | 0.4+ | 易用，支持本地部署 |
| **嵌入** | Sentence-Transformers | - | 高质量嵌入模型 |
| **网格** | Gmsh | 4.15+ | 开源，功能强大 |
| **求解** | CalculiX | - | 开源 FEA 求解器 |
| **可视化** | PyVista | 0.44+ | 基于 VTK，易用 |

### AI/LLM 技术栈

| 提供商 | 技术 | 用途 |
|--------|------|------|
| Ollama | llama.cpp | 本地模型推理 |
| OpenAI | openai SDK | GPT 系列模型 |
| Anthropic | anthropic SDK | Claude 系列模型 |
| GGUF | llama-cpp-python | 本地 GGUF 推理 |

### 前端技术栈

| 平台 | 技术 | 说明 |
|------|------|------|
| GUI | PyWebView + HTML/CSS/JS | 桌面应用 |
| Web | Jinja2 + Bootstrap | Web 界面 |
| TUI | Textual | 终端 UI |

---

## 扩展开发

### 添加新的 AI 提供商

1. 创建提供商类：

```python
# mechforge_ai/providers/custom.py
from .base import BaseProvider

class CustomProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        
    async def chat(self, messages, stream=True):
        # 实现对话逻辑
        pass
        
    async def embed(self, text):
        # 实现嵌入逻辑
        pass
```

2. 注册提供商：

```python
# mechforge_ai/providers/__init__.py
from .custom import CustomProvider

PROVIDERS = {
    "custom": CustomProvider,
}
```

### 添加新的文档加载器

1. 创建加载器类：

```python
# mechforge_knowledge/loaders/custom.py
from .base import BaseLoader

class CustomLoader(BaseLoader):
    def load(self, file_path):
        # 实现文档加载逻辑
        pass
```

2. 注册加载器：

```python
# mechforge_knowledge/loaders/__init__.py
LOADERS = {
    ".custom": CustomLoader,
}
```

### 添加 MCP 工具

1. 创建工具类：

```python
# mechforge_core/mcp/tools/custom.py
from ..base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具"
    
    def execute(self, **kwargs):
        # 实现工具逻辑
        pass
```

2. 注册工具：

```python
# mechforge_core/mcp/tools/__init__.py
TOOLS = {
    "custom_tool": CustomTool,
}
```

---

## 性能优化

### 缓存策略

| 缓存类型 | 用途 | TTL |
|----------|------|-----|
| 内存缓存 | 热点数据 | 5 分钟 |
| 文件缓存 | 嵌入向量 | 24 小时 |
| 数据库缓存 | 对话历史 | 永久 |

### 异步处理

```python
# 异步 LLM 调用
async def chat_async(messages):
    async for chunk in llm_client.stream(messages):
        yield chunk

# 异步 RAG 检索
async def retrieve_async(query):
    results = await rag_engine.search(query)
    return results
```

### 并发控制

```python
# Web 服务并发
app = FastAPI()
app.add_middleware(
    SecurityMiddleware,
    rate_limit=60,  # 每分钟 60 次
)
```

---

## 部署架构

### 单机部署

```
┌─────────────────────────────────┐
│          单机部署                │
│                                 │
│  ┌─────────┐  ┌─────────────┐  │
│  │ Ollama  │  │ MechForge   │  │
│  │ :11434  │  │ Web :8765   │  │
│  └─────────┘  └─────────────┘  │
│                                 │
│  ┌─────────────────────────┐   │
│  │ SQLite + ChromaDB       │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

### Docker 部署

```yaml
# docker-compose.yml
services:
  mechforge:
    image: ghcr.io/yd5768365-hue/mechforge:latest
    ports:
      - "8765:8765"
    volumes:
      - ./knowledge:/app/knowledge
      - ./config.yaml:/app/config.yaml
    environment:
      - OLLAMA_URL=http://ollama:11434
      
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

---

## 更多帮助

- [使用指南](USAGE.md)
- [配置说明](CONFIG.md)
- [API 文档](API.md)