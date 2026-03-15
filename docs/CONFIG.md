# MechForge AI 配置说明

本文档详细介绍 MechForge AI 的配置方式和选项。

---

## 目录

- [配置文件](#配置文件)
- [配置优先级](#配置优先级)
- [AI 模型配置](#ai-模型配置)
- [知识库配置](#知识库配置)
- [CAE 配置](#cae-配置)
- [Web 服务配置](#web-服务配置)
- [日志配置](#日志配置)
- [环境变量](#环境变量)

---

## 配置文件

### 配置文件位置

MechForge AI 支持多个配置文件位置，按优先级排序：

| 优先级 | 位置 | 说明 |
|--------|------|------|
| 1 | `./config.yaml` | 当前目录 |
| 2 | `~/.mechforge/config.yaml` | 用户目录 |
| 3 | `/etc/mechforge/config.yaml` | 系统目录 (Linux) |

### 配置文件格式

使用 YAML 格式：

```yaml
# config.yaml - MechForge AI 配置文件

# AI 提供商配置
provider:
  default: "ollama"
  
  ollama:
    url: "http://localhost:11434"
    model: "qwen2.5:3b"
    
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-opus-20240229"

# RAG 知识库配置
rag:
  enabled: false
  knowledge_path: "./knowledge"
  embedding_model: "BAAI/bge-small-zh-v1.5"
  chunk_size: 500
  chunk_overlap: 50
  top_k: 5

# CAE 工作台配置
cae:
  mesh_size: 5.0
  solver: "calculix"
  output_dir: "./output"

# Web 服务配置
web:
  host: "127.0.0.1"
  port: 8765
  reload: false

# 日志配置
logging:
  level: "INFO"
  file: "./logs/mechforge.log"
  format: "json"
```

---

## 配置优先级

配置项的优先级从高到低：

```
环境变量 > 命令行参数 > 配置文件 > 默认值
```

### 示例

```bash
# 配置文件中设置端口为 8765
# 环境变量覆盖
export MECHFORGE_WEB_PORT=9000

# 命令行参数优先级最高
mechforge-web --port 8080  # 实际使用 8080
```

---

## AI 模型配置

### Ollama 配置

```yaml
provider:
  ollama:
    url: "http://localhost:11434"  # Ollama 服务地址
    model: "qwen2.5:3b"            # 默认模型
    timeout: 60                    # 请求超时 (秒)
    stream: true                   # 流式响应
```

**环境变量**:
- `OLLAMA_URL`: Ollama 服务地址
- `OLLAMA_MODEL`: 默认模型

**常用模型**:

| 模型 | 大小 | 说明 |
|------|------|------|
| `qwen2.5:1.5b` | ~1GB | 轻量级，速度快 |
| `qwen2.5:3b` | ~2GB | 平衡性能 |
| `qwen2.5:7b` | ~4GB | 高质量输出 |
| `llama3.2:3b` | ~2GB | Meta Llama |
| `deepseek-r1:7b` | ~4GB | DeepSeek 推理 |

### OpenAI 配置

```yaml
provider:
  openai:
    api_key: "${OPENAI_API_KEY}"   # 从环境变量读取
    model: "gpt-4"
    base_url: ""                   # 可选：自定义 API 地址
    temperature: 0.7
    max_tokens: 4096
```

**环境变量**:
- `OPENAI_API_KEY`: API 密钥 (必需)
- `OPENAI_BASE_URL`: 自定义 API 地址

**可用模型**:
- `gpt-4`: GPT-4
- `gpt-4-turbo`: GPT-4 Turbo
- `gpt-3.5-turbo`: GPT-3.5 Turbo

### Anthropic 配置

```yaml
provider:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-opus-20240229"
    max_tokens: 4096
```

**环境变量**:
- `ANTHROPIC_API_KEY`: API 密钥 (必需)

**可用模型**:
- `claude-3-opus-20240229`: Claude 3 Opus
- `claude-3-sonnet-20240229`: Claude 3 Sonnet
- `claude-3-haiku-20240307`: Claude 3 Haiku

### GGUF 本地模型配置

```yaml
provider:
  gguf:
    model_path: "./models/qwen2.5-3b.gguf"
    n_ctx: 4096           # 上下文长度
    n_gpu_layers: 35      # GPU 层数 (-1 全部)
    n_threads: 4          # CPU 线程数
    temperature: 0.7
```

---

## 知识库配置

### RAG 配置

```yaml
rag:
  enabled: true                          # 启用 RAG
  knowledge_path: "./knowledge"          # 知识库路径
  index_path: "./.cache/chroma"          # 索引缓存路径
  
  # 嵌入模型
  embedding:
    model: "BAAI/bge-small-zh-v1.5"      # 嵌入模型
    device: "cpu"                         # cpu / cuda
    
  # 文档切分
  chunk:
    size: 500                             # 块大小
    overlap: 50                           # 重叠字符数
    
  # 检索配置
  retrieval:
    top_k: 5                              # 返回结果数
    mode: "hybrid"                        # vector / bm25 / hybrid
    rerank: true                          # 启用重排序
```

### 知识库目录结构

```
knowledge/
├── 机械设计/
│   ├── 齿轮设计.md
│   └── 轴承选型.pdf
├── 材料力学/
│   └── 应力分析.md
└── config.yaml          # 可选：子目录配置
```

### 嵌入模型选择

| 模型 | 大小 | 语言 | 说明 |
|------|------|------|------|
| `BAAI/bge-small-zh-v1.5` | ~100MB | 中文 | 推荐，速度快 |
| `BAAI/bge-base-zh-v1.5` | ~400MB | 中文 | 更高质量 |
| `sentence-transformers/all-MiniLM-L6-v2` | ~80MB | 英文 | 英文场景 |

---

## CAE 配置

### 网格配置

```yaml
cae:
  mesh:
    default_size: 5.0          # 默认网格尺寸
    min_size: 0.1              # 最小尺寸
    max_size: 100.0            # 最大尺寸
    algorithm: "Frontal-Delaunay"  # 网格算法
    order: 2                   # 网格阶数 (1=线性, 2=二次)
```

### 求解器配置

```yaml
cae:
  solver:
    type: "calculix"           # calculix / code_aster
    executable: "ccx"          # 求解器路径
    threads: 4                 # 并行线程数
    timeout: 3600              # 超时时间 (秒)
```

### 输出配置

```yaml
cae:
  output:
    dir: "./output"            # 输出目录
    format: "vtk"              # vtk / med / frd
    save_mesh: true            # 保存网格文件
    save_results: true         # 保存结果文件
```

---

## Web 服务配置

### 基本配置

```yaml
web:
  host: "127.0.0.1"            # 绑定地址
  port: 8765                   # 端口号
  reload: false                # 热重载 (开发模式)
  workers: 1                   # 工作进程数
  timeout: 60                  # 请求超时 (秒)
```

### 安全配置

```yaml
web:
  security:
    rate_limit: 60             # 每分钟请求数限制
    max_request_size: 10485760 # 最大请求大小 (10MB)
    
    cors:
      enabled: true
      origins: ["*"]           # 允许的来源
      
    ip_filter:
      enabled: false
      whitelist: []            # IP 白名单
      blacklist: []            # IP 黑名单
```

### WebSocket 配置

```yaml
web:
  websocket:
    enabled: true
    ping_interval: 30          # 心跳间隔 (秒)
    ping_timeout: 10           # 心跳超时 (秒)
    max_size: 1048576          # 最大消息大小 (1MB)
```

---

## 日志配置

### 基本配置

```yaml
logging:
  level: "INFO"                # DEBUG / INFO / WARNING / ERROR
  file: "./logs/mechforge.log" # 日志文件路径
  format: "json"               # text / json
  rotation: "10 MB"            # 日志轮转大小
  retention: "7 days"          # 日志保留时间
```

### 日志级别

| 级别 | 说明 |
|------|------|
| `DEBUG` | 详细调试信息 |
| `INFO` | 一般信息 |
| `WARNING` | 警告信息 |
| `ERROR` | 错误信息 |
| `CRITICAL` | 严重错误 |

### 模块日志级别

```yaml
logging:
  level: "INFO"
  modules:
    mechforge_ai: "DEBUG"
    mechforge_web: "WARNING"
    mechforge_work: "INFO"
```

---

## 环境变量

### 完整环境变量列表

| 变量 | 默认值 | 说明 |
|------|--------|------|
| **AI 模型** |||
| `OLLAMA_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | 默认 Ollama 模型 |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `OPENAI_BASE_URL` | - | OpenAI API 地址 |
| `ANTHROPIC_API_KEY` | - | Anthropic API Key |
| **知识库** |||
| `MECHFORGE_RAG` | `false` | 启用 RAG |
| `MECHFORGE_KNOWLEDGE_PATH` | `./knowledge` | 知识库路径 |
| `MECHFORGE_EMBEDDING_MODEL` | `BAAI/bge-small-zh-v1.5` | 嵌入模型 |
| **CAE** |||
| `MECHFORGE_MESH_SIZE` | `5.0` | 默认网格尺寸 |
| `MECHFORGE_SOLVER` | `calculix` | 求解器类型 |
| **Web** |||
| `MECHFORGE_WEB_HOST` | `127.0.0.1` | Web 绑定地址 |
| `MECHFORGE_WEB_PORT` | `8765` | Web 端口 |
| **其他** |||
| `MECHFORGE_LOG_LEVEL` | `info` | 日志级别 |
| `MECHFORGE_THEME` | `dark` | UI 主题 |
| `MECHFORGE_CONFIG` | - | 配置文件路径 |
| `MECHFORGE_CACHE_DIR` | `~/.mechforge/cache` | 缓存目录 |

### .env 文件

创建 `.env` 文件管理环境变量：

```bash
# .env - MechForge AI 环境变量

# AI 提供商
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx

# 知识库
MECHFORGE_RAG=true
MECHFORGE_KNOWLEDGE_PATH=./knowledge

# Web 服务
MECHFORGE_WEB_PORT=8765

# 日志
MECHFORGE_LOG_LEVEL=debug
```

---

## 配置示例

### 开发环境配置

```yaml
# config.dev.yaml
provider:
  default: "ollama"
  ollama:
    model: "qwen2.5:3b"

rag:
  enabled: true
  knowledge_path: "./knowledge"

web:
  host: "127.0.0.1"
  port: 8765
  reload: true

logging:
  level: "DEBUG"
```

### 生产环境配置

```yaml
# config.prod.yaml
provider:
  default: "openai"
  openai:
    model: "gpt-4"

rag:
  enabled: true
  knowledge_path: "/data/knowledge"

web:
  host: "0.0.0.0"
  port: 80
  workers: 4
  
  security:
    rate_limit: 100
    cors:
      origins: ["https://example.com"]

logging:
  level: "INFO"
  file: "/var/log/mechforge/app.log"
```

---

## 配置验证

### 检查配置

```bash
# 验证配置文件
mechforge --validate-config

# 显示当前配置
mechforge --show-config
```

### 常见配置错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `API Key 未设置` | 未配置 API 密钥 | 设置环境变量或配置文件 |
| `Ollama 连接失败` | Ollama 服务未启动 | 运行 `ollama serve` |
| `知识库路径不存在` | 路径错误 | 创建目录或修改配置 |
| `端口被占用` | 端口冲突 | 更换端口或关闭占用进程 |

---

## 更多帮助

- [使用指南](USAGE.md)
- [API 文档](API.md)
- [架构文档](ARCHITECTURE.md)