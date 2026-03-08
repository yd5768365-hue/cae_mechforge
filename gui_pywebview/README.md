# MechForge AI PyWebView 桌面应用

轻量级跨平台桌面应用，使用 PyWebView 替代 PySide6。

## 优势

- **更轻量**: 无需 Qt 依赖，安装包更小
- **原生体验**: 使用系统 WebView（Windows: Edge WebView2）
- **跨平台**: 支持 Windows、macOS、Linux
- **简洁 API**: 代码更简洁，易于维护

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
bash start.sh
```

**或直接运行:**
```bash
python desktop_app.py
```

## 项目结构

```
gui_pywebview/
├── desktop_app.py      # 主入口文件
├── server.py           # FastAPI 后端服务器
├── index.html          # 前端页面
├── styles.css          # 样式文件
├── app.js              # 前端逻辑
├── core/               # 核心模块
│   ├── api-client.js   # API 客户端
│   └── event-bus.js    # 事件总线
├── services/           # 服务模块
│   ├── ai-service.js   # AI 服务
│   └── config-service.js # 配置服务
├── dj-whale.png        # 应用图标
├── start.bat           # Windows 启动脚本
├── start.sh            # Linux/macOS 启动脚本
├── build.py            # 打包脚本
├── build.bat           # Windows 打包脚本
└── requirements.txt    # 依赖列表
```

## 打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
python build.py --build
```

打包后的可执行文件位于 `dist/` 目录。

## 与 PySide6 版本对比

| 特性 | PyWebView | PySide6 |
|------|-----------|---------|
| 安装包大小 | ~50MB | ~200MB |
| 依赖复杂度 | 低 | 高 |
| 启动速度 | 快 | 中等 |
| 内存占用 | 低 | 高 |
| GPU 兼容性 | 好 | 需要配置 |
| 跨平台 | 优秀 | 优秀 |

## 技术栈

- **前端**: HTML/CSS/JavaScript
- **后端**: FastAPI + Uvicorn
- **桌面框架**: PyWebView
- **渲染引擎**: 系统 WebView

## 许可证

MIT License