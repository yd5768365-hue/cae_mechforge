# MechForge AI

<p align="center">
  <img src="docs/images/logo.png" alt="MechForge Logo" width="200"/>
</p>

<p align="center">
  <strong>真正懂机械、敢说真话、能真算</strong>
</p>

<p align="center">
  机械系苦逼在校生，用代码修补现实的缝隙 🔧🤖
</p>

<p align="center">
  <a href="https://github.com/yd5768365-hue/mechforge/releases">
    <img src="https://img.shields.io/badge/version-0.4.0-blue.svg" alt="Version"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python"/>
  </a>
</p>

---

## 📚 文档中心

> 所有文档统一管理，点击链接即可查看

### 核心文档

| 文档 | 说明 | 链接 |
|------|------|------|
| 📖 项目介绍 | 功能概述、快速开始 | [README.md](README.md) |
| 📦 安装指南 | 环境配置、依赖安装 | [INSTALL.md](INSTALL.md) |
| 📝 更新日志 | 版本历史、变更记录 | [CHANGELOG.md](开发日志/CHANGELOG.md) |
| 🔧 开发日志 | 开发经历、问题解决 | [DEV_LOG.md](开发日志/DEV_LOG.md) |
| 🐳 Docker 部署 | 容器化部署指南 | [DOCKER.md](docs/DOCKER.md) |

### 模块文档

| 模块 | 说明 | 链接 |
|------|------|------|
| 🤖 AI 对话 | LLM 客户端、MCP 工具 | [mechforge_ai/](mechforge_ai/) |
| 📚 知识库 | RAG 引擎、向量检索 | [mechforge_knowledge/](mechforge_knowledge/) |
| ⚙️ CAE 工作台 | 网格划分、FEA 求解 | [mechforge_work/](mechforge_work/) |
| 🌐 Web 服务 | FastAPI、WebSocket | [mechforge_web/](mechforge_web/) |
| 🖥️ GUI 应用 | PyWebView 桌面界面 | [gui_pywebview/](gui_pywebview/) |
| 🎨 主题组件 | UI 组件、样式 | [mechforge_theme/](mechforge_theme/) |
| 🔧 核心模块 | 配置、日志、缓存 | [mechforge_core/](mechforge_core/) |

### AI 助手配置

| 文档 | 说明 | 链接 |
|------|------|------|
| 🤖 Qwen 配置 | 项目上下文、开发规范 | [QWEN.md](QWEN.md) |
| 🤖 Claude 配置 | 项目上下文 | [CLAUDE.md](CLAUDE.md) |
| 🔌 MCP 配置 | 工具调用协议 | [mcp_config.json](mcp_config.json) |

### 开发报告

| 文档 | 说明 | 链接 |
|------|------|------|
| 📊 GUI 实现总结 | PyWebView 开发经历 | [GUI_AI_实现总结.md](开发日志/2026-03-08_GUI_AI_实现总结.md) |
| 📊 GUI 完成报告 | 功能实现报告 | [GUI_AI_完成报告.md](docs/GUI_AI_完成报告.md) |
| 📊 功能检查报告 | 项目功能验证 | [项目功能检查报告.md](docs/项目功能检查报告.md) |

---

## 🖥️ 界面展示

### 1. AI 对话模式

<p align="center">
  <img src="docs/images/ai_chat.png" alt="AI 对话模式" width="600"/>
</p>

**启动命令**: `mechforge` 或 `mechforge-gui`

**功能特性**:
- 🤖 多模型支持: OpenAI, Anthropic, Ollama, GGUF
- 💬 流式响应，实时打字机效果
- 🔧 MCP 工具调用，内置工程计算
- 📚 RAG 知识库检索集成

**相关文档**:
- [AI 模块文档](mechforge_ai/)
- [模型管理 CLI](mechforge_ai/model_cli.py)

**开发经历**:
- [2026-03-04 RAG 引擎优化](开发日志/DEV_LOG.md#2026年3月4日)

---

### 2. 知识库模式

<p align="center">
  <img src="docs/images/knowledge.png" alt="知识库模式" width="600"/>
</p>

**启动命令**: `mechforge-k`

**功能特性**:
- 📚 RAG 引擎: 向量检索 + BM25 + 重排序
- 📄 多格式支持: Markdown, PDF, TXT, Word
- 🔍 原文呈现，杜绝 AI 幻觉
- 🏷️ 智能切分，自动文档分块

**相关文档**:
- [知识库模块文档](mechforge_knowledge/)
- [RAGFlow 集成指南](#-ragflow-集成指南)

**开发经历**:
- [知识库后端架构设计](开发日志/DEV_LOG.md)

---

### 3. CAE 工作台

<p align="center">
  <img src="docs/images/cae_workbench.png" alt="CAE 工作台" width="600"/>
</p>

**启动命令**: `mechforge-work`

**功能特性**:
- 🔧 几何处理: STEP, IGES, STL, BREP 导入
- 📐 网格划分: Gmsh 4.15+ 集成
- ⚙️ FEA 求解: CalculiX 本地求解
- 📊 可视化: PyVista 3D 云图

**交互命令**:
```
/demo      - 运行悬臂梁示例
/load      - 加载几何文件
/mesh      - 生成网格
/solve     - 执行求解
/show      - 可视化结果
/export    - 导出结果
```

**相关文档**:
- [CAE 模块文档](mechforge_work/)
- [Gmsh 网格引擎](mechforge_work/mesh_engine.py)

**开发经历**:
- [CAE 工作台实现](开发日志/DEV_LOG.md)

---

### 4. Web 界面

<p align="center">
  <em>Web 界面截图待添加</em>
</p>

**启动命令**: `mechforge-web`

**功能特性**:
- 🌐 FastAPI 高性能异步后端
- 🔌 WebSocket 实时双向通信
- 🔒 安全中间件: 速率限制、IP 过滤
- 📱 响应式设计

**访问地址**: http://localhost:8080

**相关文档**:
- [Web 模块文档](mechforge_web/)
- [API 文档](mechforge_web/api.py)

**开发经历**:
- [Web 服务开发](开发日志/DEV_LOG.md)

---

### 5. GUI 桌面应用

<p align="center">
  <em>GUI 演示视频待添加: docs/images/gui_demo.mp4</em>
</p>

**启动命令**: `mechforge-gui`

**功能特性**:
- 🎨 科幻控制台风格主题
- 🌌 深空蓝背景 + 霓虹青强调色
- ✨ Modern Dark Glassmorphism 设计
- 🤖 AI 对话、知识库、CAE 工作台、经验库集成
- 📦 单文件打包 (~71MB)

**界面模块**:
| 模块 | 功能 |
|------|------|
| AI 助手 | 多模型对话、流式响应、MCP 工具调用 |
| 知识库 | RAG 检索、书籍轮播、分类标签 |
| CAE 工作台 | 模型加载、网格划分、求解可视化 |
| 经验库 | 故障案例、Daily Feed 知识推送 |
| 设置 | API 配置、主题切换、知识库路径 |

**相关文档**:
- [GUI 模块文档](gui_pywebview/)
- [主题设计](gui_pywebview/css/industrial-theme.css)

**开发经历**:
- [2026-03-08 GUI AI 实现总结](开发日志/2026-03-08_GUI_AI_实现总结.md)

---

## 🚀 快速开始

### 安装

```bash
# PyPI 安装
pip install mechforge-ai

# 完整安装
pip install mechforge-ai[all]

# 从源码安装
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
pip install -e ".[all]"
```

### 命令速查

| 命令 | 功能 | 说明 |
|------|------|------|
| `mechforge` | AI 对话 | 终端交互模式 |
| `mechforge-gui` | GUI 应用 | 桌面图形界面 |
| `mechforge-k` | 知识库 | RAG 检索模式 |
| `mechforge-work` | CAE 工作台 | 有限元分析 |
| `mechforge-web` | Web 服务 | 浏览器访问 |
| `mechforge-model` | 模型管理 | Ollama/GGUF |

---

## 📦 Docker 部署

```bash
# Docker Compose (推荐)
docker-compose --profile full up -d

# 单独模式
docker-compose --profile ai up -d     # AI 对话
docker-compose --profile rag up -d    # 知识库
docker-compose --profile work up -d   # CAE 工作台
docker-compose --profile web up -d    # Web 服务
```

**镜像变体**:
| 镜像 | 大小 | 描述 |
|------|------|------|
| `ghcr.io/yd5768365-hue/mechforge:latest` | ~800MB | 完整版 |
| `ghcr.io/yd5768365-hue/mechforge-ai:latest` | ~200MB | AI 对话 |
| `ghcr.io/yd5768365-hue/mechforge-rag:latest` | ~500MB | 知识库 |
| `ghcr.io/yd5768365-hue/mechforge-work:latest` | ~400MB | CAE 工作台 |
| `ghcr.io/yd5768365-hue/mechforge-web:latest` | ~300MB | Web 服务 |

---

## 📂 项目结构

```
mechforge_ai/
├── mechforge_core/          # 核心模块 (配置、缓存、数据库、日志)
├── mechforge_ai/            # AI 对话模块
├── mechforge_knowledge/     # 知识库模块
├── mechforge_work/          # CAE 工作台模块
├── mechforge_web/           # Web 服务模块
├── gui_pywebview/           # GUI 桌面应用
├── mechforge_theme/         # 主题组件
├── docs/                    # 文档
├── 开发日志/                # 开发日志
├── tests/                   # 测试
├── examples/                # 示例
└── scripts/                 # 脚本
```

---

## 📝 更新日志

### v0.4.0 (2026-03-15)

**新特性**:
- GUI 桌面应用科幻主题
- 知识库路径统一管理
- RAG 功能完整支持
- 反思引擎集成

**修复**:
- RAG 引擎启动延迟
- mechforge-work 入口点参数错误

👉 [查看完整更新日志](开发日志/CHANGELOG.md)

---

## 📞 联系方式

- **GitHub**: https://github.com/yd5768365-hue/mechforge
- **Issues**: [报告问题](https://github.com/yd5768365-hue/mechforge/issues)

---

<p align="center">
  Made with ❤️ for Mechanical Engineers
</p>