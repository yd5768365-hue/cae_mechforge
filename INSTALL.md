# MechForge AI - 安装指南

## 📋 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10/11, Linux, macOS | Windows 11 64位 |
| Python | 3.10+ | 3.11+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘空间 | 500 MB | 2 GB+ (含模型) |
| 网络 | 可选 | 宽带连接 |

---

## 🚀 快速安装

### 方式一：PyPI 安装（推荐）

```bash
# 基础安装
pip install mechforge-ai

# 完整安装（包含所有功能）
pip install mechforge-ai[all]
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装
pip install -e ".[all]"
```

---

## 📦 依赖分组

| 分组 | 用途 | 安装命令 |
|------|------|----------|
| 基础 | 核心功能 | `pip install mechforge-ai` |
| dev | 开发工具 | `pip install mechforge-ai[dev]` |
| llm | GGUF 推理 | `pip install mechforge-ai[llm]` |
| rag | 知识库 RAG | `pip install mechforge-ai[rag]` |
| work | CAE 工作台 | `pip install mechforge-ai[work]` |
| web | Web 服务 | `pip install mechforge-ai[web]` |
| all | 完整功能 | `pip install mechforge-ai[all]` |

---

## 🤖 AI 模型配置

### Ollama（本地推荐）

1. **安装 Ollama**
   ```bash
   # Windows
   winget install Ollama.Ollama
   
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **下载模型**
   ```bash
   # 推荐模型
   ollama pull qwen2.5:1.5b    # 轻量级 (~1GB)
   ollama pull qwen2.5:3b      # 平衡 (~2GB)
   ollama pull qwen2.5:7b      # 高质量 (~4GB)
   ```

3. **启动服务**
   ```bash
   ollama serve
   ```

### OpenAI

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key"
```

或在 `config.yaml` 中配置：
```yaml
provider:
  default: "openai"
  openai:
    api_key: "your-api-key"
    model: "gpt-4o-mini"
```

### Anthropic

```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key"
```

### GGUF 本地模型

```bash
# 下载 GGUF 模型到 models/ 目录
# 然后在设置中选择 GGUF 提供商
```

---

## ⚙️ 配置文件

### 配置位置

| 系统 | 路径 |
|------|------|
| Windows | `%USERPROFILE%\.mechforge\config.yaml` |
| Linux/macOS | `~/.mechforge/config.yaml` |
| 项目目录 | `./config.yaml` |

### 配置示例

```yaml
# AI 提供商配置
provider:
  default: "ollama"
  ollama:
    url: "http://localhost:11434"
    model: "qwen2.5:3b"
  openai:
    api_key: ""
    model: "gpt-4o-mini"
  anthropic:
    api_key: ""
    model: "claude-3-haiku-20240307"

# 知识库配置
knowledge:
  path: "./knowledge"
  rag_enabled: true

# 日志配置
logging:
  level: "info"
  file: "./logs/mechforge.log"

# UI 配置
ui:
  theme: "dark"
  language: "zh-CN"
```

---

## 🐳 Docker 安装

### Docker Compose（推荐）

```bash
# 完整部署
docker-compose --profile full up -d

# 单独部署
docker-compose --profile ai up -d     # AI 对话
docker-compose --profile rag up -d    # 知识库
docker-compose --profile work up -d   # CAE 工作台
docker-compose --profile web up -d    # Web 服务
```

### Docker 命令

```bash
# 拉取镜像
docker pull ghcr.io/yd5768365-hue/mechforge:latest

# 运行容器
docker run -d \
  --name mechforge \
  -p 8080:8080 \
  -v ./knowledge:/app/knowledge \
  ghcr.io/yd5768365-hue/mechforge:latest
```

---

## 📚 知识库配置

### 添加知识库文件

1. 创建知识库目录：
   ```bash
   mkdir knowledge
   ```

2. 添加文档文件：
   - Markdown (.md)
   - PDF (.pdf)
   - 文本 (.txt)
   - Word (.docx)

3. 启用 RAG：
   ```bash
   export MECHFORGE_RAG=true
   # 或在 config.yaml 中设置 knowledge.rag_enabled: true
   ```

### 示例知识库

创建 `knowledge/机械设计手册.md`：
```markdown
# 机械设计手册

## 材料属性

### Q235 钢
- 屈服强度: 235 MPa
- 抗拉强度: 375-500 MPa
- 弹性模量: 206 GPa

### 45 钢
- 屈服强度: 355 MPa
- 抗拉强度: 600 MPa
- 弹性模量: 206 GPa
```

---

## ⚙️ CAE 工作台配置

### 安装依赖

```bash
# 安装 CAE 相关依赖
pip install mechforge-ai[work]
```

### 外部工具

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| Gmsh 4.15+ | 网格划分 | `pip install gmsh` |
| CalculiX | FEA 求解 | [官网下载](http://www.dhondt.de/) |
| PyVista | 3D 可视化 | `pip install pyvista` |

### 验证安装

```bash
mechforge-work demo
```

---

## 🛠️ 故障排除

### 问题：pip 安装失败

**解决方案:**
```bash
# 使用国内镜像
pip install mechforge-ai -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：Ollama 连接失败

**解决方案:**
```bash
# 检查 Ollama 服务
ollama --version

# 启动服务
ollama serve

# 检查端口
netstat -an | grep 11434
```

### 问题：模型下载慢

**解决方案:**
```bash
# 配置代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### 问题：CAE 功能不可用

**解决方案:**
```bash
# 检查环境
python check_env.py

# 安装缺失依赖
pip install gmsh pyvista
```

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/yd5768365-hue/mechforge/issues
- **文档**: [README.md](README.md)
- **开发日志**: [DEV_LOG.md](开发日志/DEV_LOG.md)

---

**版本**: 0.4.0  
**更新日期**: 2026-03-15