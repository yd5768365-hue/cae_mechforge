# MechForge AI - 故障排除指南

## HTTP 连接失败问题

### 症状
- 控制台显示 "Failed to link HTTP"
- API 请求返回模拟数据
- 聊天功能不工作

### 原因

#### 1. 直接打开 HTML 文件（最常见）
**错误做法：**
```
双击打开 index.html
```

**结果：**
- URL: `file:///D:/.../index.html`
- Protocol: `file:`
- API 使用模拟数据

**正确做法：**
```bash
# 方法 1: 使用桌面应用（推荐）
python desktop_app.py

# 方法 2: 先启动后端服务器
python server.py
# 然后浏览器访问 http://localhost:5000

# 方法 3: Windows 用户
start.bat
```

### 诊断步骤

#### 步骤 1: 检查控制台输出
打开浏览器开发者工具 (F12) → Console，查看：

**正常情况（桌面应用）：**
```
[APIClient] Initialized: {
  baseURL: "http://127.0.0.1:5000/api",
  protocol: "http:",
  isLocalFile: false
}
```

**错误情况（直接打开文件）：**
```
⚠️ WARNING: Running in local file mode (file://)
   API calls will use mock data instead of real backend.
```

#### 步骤 2: 运行连接测试
在浏览器控制台执行：
```javascript
// 加载诊断脚本
const script = document.createElement('script');
script.src = 'scripts/connection-test.js';
document.head.appendChild(script);
```

#### 步骤 3: 检查后端是否运行
```bash
# 测试后端健康检查
curl http://localhost:5000/api/health

# 应该返回 JSON 数据
```

### 解决方案

#### 方案 1: 使用桌面应用（推荐）

```bash
# 安装依赖
pip install pywebview fastapi uvicorn

# 启动桌面应用
python desktop_app.py
```

桌面应用会自动：
1. 启动后端服务器（在随机可用端口）
2. 打开 PyWebView 窗口
3. 正确加载前端（http://127.0.0.1:port）

#### 方案 2: 手动启动后端

```bash
# 终端 1: 启动后端
python server.py
# 输出: Uvicorn running on http://0.0.0.0:5000

# 终端 2: 浏览器访问
# 打开 http://localhost:5000
```

#### 方案 3: 使用 Node.js 静态服务器

```bash
# 如果没有 Python 后端，但需要测试前端
npx serve .

# 然后访问 http://localhost:3000
# ⚠️ 注意：这只能测试 UI，没有后端功能
```

### 常见问题

#### Q: 为什么直接打开 HTML 文件不行？
**A:** 现代浏览器安全策略（CORS）禁止 `file://` 协议的页面访问 HTTP API。

#### Q: PyWebView 和直接打开有什么区别？
**A:** 
- 直接打开：`file:///path/to/index.html` → 无法访问 API
- PyWebView：`http://127.0.0.1:5000/` → 正常访问 API

#### Q: 如何确认我在使用正确的模式？
**A:** 查看浏览器控制台：
- ✅ `protocol: "http:"` - 正确
- ❌ `protocol: "file:"` - 错误

#### Q: 端口被占用怎么办？
**A:** 桌面应用会自动寻找可用端口（从 5000 开始）。手动启动时可以指定端口：
```bash
python server.py --port 8080
```

### 错误代码参考

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Failed to fetch` | 后端未启动 | 运行 `python desktop_app.py` |
| `CORS error` | 跨域问题 | 已修复，使用最新代码 |
| `Request timeout` | 后端响应慢 | 检查后端日志 |
| `isLocalFile: true` | 直接打开 HTML | 使用桌面应用 |

### 调试技巧

#### 1. 查看网络请求
```
F12 → Network → 查看请求是否发出
```

#### 2. 检查后端日志
```bash
# 后端启动时会显示日志
python server.py
# 查看是否有请求到达
```

#### 3. 测试 API
```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 测试聊天
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### 联系支持

如果以上方法都无法解决问题：
1. 查看 `docs/DEV_LOG.md` 开发日志
2. 提交 Issue 到 GitHub
3. 附上控制台输出和错误信息
