# MechForge AI 使用指南

本文档详细介绍 MechForge AI 各模块的使用方法和命令参数。

---

## 目录

- [命令概览](#命令概览)
- [AI 对话模式](#ai-对话模式)
- [知识库模式](#知识库模式)
- [CAE 工作台](#cae-工作台)
- [Web 服务](#web-服务)
- [GUI 桌面应用](#gui-桌面应用)
- [模型管理](#模型管理)

---

## 命令概览

| 命令 | 功能 | 入口文件 |
|------|------|----------|
| `mechforge` | AI 对话 (终端) | `mechforge_ai/terminal.py` |
| `mechforge-gui` | GUI 桌面应用 | `gui_pywebview/main.py` |
| `mechforge-k` | 知识库检索 | `mechforge_knowledge/cli.py` |
| `mechforge-work` | CAE 工作台 | `mechforge_work/work_cli.py` |
| `mechforge-web` | Web 服务 | `mechforge_web/main.py` |
| `mechforge-model` | 模型管理 | `mechforge_ai/model_cli.py` |

---

## AI 对话模式

### 启动命令

```bash
# 终端交互模式
mechforge

# 指定模型
mechforge --model qwen2.5:3b

# 启用 RAG 知识库
mechforge --rag
```

### 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--model` | `-m` | 指定模型名称 | 配置文件默认 |
| `--provider` | `-p` | 指定提供商 | ollama |
| `--rag` | `-r` | 启用 RAG 检索 | false |
| `--config` | `-c` | 配置文件路径 | ./config.yaml |
| `--verbose` | `-v` | 详细输出 | false |

### 交互命令

在对话模式下，可以使用以下命令：

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助信息 |
| `/clear` | 清空对话历史 |
| `/model <name>` | 切换模型 |
| `/provider <name>` | 切换提供商 |
| `/rag on/off` | 开关 RAG 检索 |
| `/save <file>` | 保存对话到文件 |
| `/load <file>` | 加载对话历史 |
| `/exit` | 退出程序 |

### 支持的 AI 提供商

| 提供商 | 说明 | 配置项 |
|--------|------|--------|
| **Ollama** | 本地模型服务 | `OLLAMA_URL`, `OLLAMA_MODEL` |
| **OpenAI** | GPT 系列模型 | `OPENAI_API_KEY` |
| **Anthropic** | Claude 系列模型 | `ANTHROPIC_API_KEY` |
| **GGUF** | 本地 GGUF 文件 | `GGUF_MODEL_PATH` |

### 示例

```bash
# 使用 Ollama 本地模型
mechforge --provider ollama --model qwen2.5:3b

# 使用 OpenAI API
export OPENAI_API_KEY=sk-xxx
mechforge --provider openai --model gpt-4

# 启用知识库检索
mechforge --rag --knowledge-path ./my_knowledge
```

---

## 知识库模式

### 启动命令

```bash
# 启动知识库检索
mechforge-k

# 指定知识库路径
mechforge-k --path ./knowledge

# 交互模式
mechforge-k --interactive
```

### 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--path` | `-p` | 知识库路径 | ./knowledge |
| `--interactive` | `-i` | 交互模式 | false |
| `--top-k` | `-k` | 返回结果数量 | 5 |
| `--rebuild` | | 重建索引 | false |

### 支持的文档格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Markdown | `.md` | 推荐格式，支持标题解析 |
| PDF | `.pdf` | 自动提取文本 |
| TXT | `.txt` | 纯文本文件 |
| Word | `.docx` | Microsoft Word 文档 |

### 知识库结构

```
knowledge/
├── 机械设计/
│   ├── 齿轮设计.md
│   └── 轴承选型.md
├── 材料力学/
│   └── 应力分析.md
└── 有限元分析/
    └── 网格划分.md
```

### 检索模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **向量检索** | 语义相似度匹配 | 概念性问题 |
| **BM25** | 关键词匹配 | 精确查找 |
| **混合检索** | 向量 + BM25 融合 | 综合检索 |
| **重排序** | 二次排序优化 | 高精度需求 |

---

## CAE 工作台

### 启动命令

```bash
# 启动 CAE 工作台
mechforge-work

# TUI 界面模式
mechforge-work --tui

# 运行示例
mechforge-work --demo
```

### 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--tui` | | TUI 界面模式 | false |
| `--demo` | | 运行悬臂梁示例 | false |
| `--file` | `-f` | 加载几何文件 | - |
| `--output` | `-o` | 输出目录 | ./output |

### 交互命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/demo` | 运行悬臂梁示例 | `/demo` |
| `/load <file>` | 加载几何文件 | `/load model.step` |
| `/mesh` | 生成网格 | `/mesh` |
| `/mesh-size <size>` | 设置网格尺寸 | `/mesh-size 5.0` |
| `/solve` | 执行求解 | `/solve` |
| `/show` | 可视化结果 | `/show` |
| `/export <format>` | 导出结果 | `/export vtk` |
| `/info` | 显示模型信息 | `/info` |
| `/help` | 显示帮助 | `/help` |
| `/exit` | 退出程序 | `/exit` |

### 支持的几何格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| STEP | `.step`, `.stp` | 推荐格式 |
| IGES | `.iges`, `.igs` | 通用交换格式 |
| STL | `.stl` | 三角网格 |
| BREP | `.brep` | OpenCASCADE 原生 |

### 分析流程

```
1. 加载几何 (/load)
      ↓
2. 网格划分 (/mesh)
      ↓
3. 设置边界条件
      ↓
4. 执行求解 (/solve)
      ↓
5. 可视化结果 (/show)
      ↓
6. 导出数据 (/export)
```

### 示例：悬臂梁分析

```bash
mechforge-work

# 进入后执行
/demo

# 或手动操作
/load examples/cantilever.step
/mesh-size 2.0
/mesh
/solve
/show
/export vtk
```

---

## Web 服务

### 启动命令

```bash
# 默认启动 (端口 8765)
mechforge-web

# 指定端口
mechforge-web --port 8080

# 指定绑定地址
mechforge-web --host 0.0.0.0

# 开发模式 (热重载)
mechforge-web --reload
```

### 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--host` | `-h` | 绑定地址 | 127.0.0.1 |
| `--port` | `-p` | 端口号 | 8765 |
| `--reload` | | 开发模式热重载 | false |
| `--workers` | `-w` | 工作进程数 | 1 |

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/api/chat` | POST | AI 对话 |
| `/api/knowledge` | POST | 知识库检索 |
| `/api/models` | GET | 获取模型列表 |
| `/ws/chat` | WebSocket | 实时对话 |
| `/docs` | GET | API 文档 |
| `/health` | GET | 健康检查 |

### WebSocket 使用

```javascript
// JavaScript 示例
const ws = new WebSocket('ws://localhost:8765/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'message',
    content: '你好，请介绍一下自己'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};
```

### 安全配置

Web 服务内置安全中间件：

| 功能 | 说明 |
|------|------|
| 速率限制 | 每分钟最多 60 次请求 |
| IP 过滤 | 可配置黑白名单 |
| CORS | 跨域资源共享配置 |
| 请求大小限制 | 最大 10MB |

---

## GUI 桌面应用

### 启动命令

```bash
# 启动 GUI 应用
mechforge-gui
```

### 界面模块

| 模块 | 功能 | 快捷键 |
|------|------|--------|
| AI 助手 | 多模型对话 | `Ctrl+1` |
| 知识库 | RAG 检索 | `Ctrl+2` |
| CAE 工作台 | 有限元分析 | `Ctrl+3` |
| 经验库 | 故障案例 | `Ctrl+4` |
| 设置 | 配置管理 | `Ctrl+,` |

### 设置选项

| 选项 | 说明 |
|------|------|
| **AI 提供商** | Ollama / OpenAI / Anthropic |
| **默认模型** | 选择默认使用的模型 |
| **API Key** | 配置云端 API 密钥 |
| **知识库路径** | 设置知识库目录 |
| **主题** | 深色 / 浅色主题 |
| **语言** | 中文 / English |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+N` | 新建对话 |
| `Ctrl+S` | 保存对话 |
| `Ctrl+Enter` | 发送消息 |
| `Ctrl+L` | 清空对话 |
| `Ctrl+Q` | 退出应用 |
| `F11` | 全屏模式 |

---

## 模型管理

### 查看可用模型

```bash
# 列出所有可用模型
mechforge-model list

# 查看当前模型
mechforge-model current
```

### 选择模型

```bash
# 交互式选择
mechforge-model select

# 直接指定
mechforge-model select --provider ollama --model qwen2.5:3b
```

### 下载模型

```bash
# 下载 Ollama 模型
ollama pull qwen2.5:3b

# 下载 GGUF 模型
mechforge-model download --url https://example.com/model.gguf
```

### 模型配置

```yaml
# config.yaml
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
    
  gguf:
    model_path: "./models/qwen2.5-3b.gguf"
    n_ctx: 4096
    n_gpu_layers: 35
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | 默认 Ollama 模型 |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `ANTHROPIC_API_KEY` | - | Anthropic API Key |
| `MECHFORGE_RAG` | `false` | 启用 RAG |
| `MECHFORGE_KNOWLEDGE_PATH` | `./knowledge` | 知识库路径 |
| `MECHFORGE_LOG_LEVEL` | `info` | 日志级别 |
| `MECHFORGE_THEME` | `dark` | UI 主题 |
| `MECHFORGE_WEB_PORT` | `8765` | Web 服务端口 |

---

## 常见问题

### Q: 命令未找到？

确保已激活虚拟环境或已添加到 PATH：

```bash
# 激活虚拟环境
source mechforge/bin/activate  # Linux/Mac
mechforge\Scripts\activate     # Windows

# 或重新安装
pip install --upgrade mechforge-ai
```

### Q: Ollama 连接失败？

```bash
# 检查 Ollama 服务
ollama list

# 启动 Ollama 服务
ollama serve

# 下载模型
ollama pull qwen2.5:3b
```

### Q: CAE 功能不可用？

```bash
# 安装 CAE 依赖
pip install mechforge-ai[work]

# 检查环境
python check_cae_env.py
```

### Q: 知识库检索无结果？

1. 确认知识库目录有文档文件
2. 重建索引：`mechforge-k --rebuild`
3. 检查文档格式是否支持

---

## 更多帮助

- [配置说明](CONFIG.md)
- [API 文档](API.md)
- [架构文档](ARCHITECTURE.md)
- [GitHub Issues](https://github.com/yd5768365-hue/mechforge/issues)