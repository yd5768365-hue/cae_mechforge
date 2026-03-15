# MechForge AI API 文档

本文档详细介绍 MechForge AI Web 服务的 API 接口。

---

## 目录

- [API 概览](#api-概览)
- [认证](#认证)
- [对话 API](#对话-api)
- [知识库 API](#知识库-api)
- [模型 API](#模型-api)
- [CAE API](#cae-api)
- [WebSocket API](#websocket-api)
- [错误处理](#错误处理)

---

## API 概览

### 基础信息

| 项目 | 说明 |
|------|------|
| 基础 URL | `http://localhost:8765` |
| API 前缀 | `/api` |
| 文档地址 | `http://localhost:8765/docs` |
| OpenAPI 规范 | `http://localhost:8765/openapi.json` |

### 请求格式

- Content-Type: `application/json`
- 字符编码: `UTF-8`

### 响应格式

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 通用状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 认证

### API Key 认证

```http
Authorization: Bearer YOUR_API_KEY
```

### 配置 API Key

```yaml
# config.yaml
web:
  security:
    api_key: "your-secret-key"
```

---

## 对话 API

### POST /api/chat

发送消息并获取 AI 回复。

**请求体**:

```json
{
  "message": "请介绍一下有限元分析的基本原理",
  "conversation_id": "conv_123",
  "model": "qwen2.5:3b",
  "provider": "ollama",
  "stream": true,
  "rag": {
    "enabled": true,
    "top_k": 5
  }
}
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户消息 |
| `conversation_id` | string | 否 | 会话 ID |
| `model` | string | 否 | 模型名称 |
| `provider` | string | 否 | 提供商 |
| `stream` | boolean | 否 | 是否流式响应 |
| `rag.enabled` | boolean | 否 | 启用 RAG |
| `rag.top_k` | integer | 否 | RAG 返回数量 |

**响应 (非流式)**:

```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_123",
    "message": {
      "role": "assistant",
      "content": "有限元分析是一种数值分析方法...",
      "timestamp": "2026-03-15T10:30:00Z"
    },
    "model": "qwen2.5:3b",
    "provider": "ollama"
  }
}
```

**响应 (流式)**:

```
data: {"content": "有限元", "done": false}
data: {"content": "分析", "done": false}
data: {"content": "是一种", "done": false}
data: {"content": "", "done": true}
```

### GET /api/conversations

获取会话列表。

**响应**:

```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_123",
        "title": "有限元分析讨论",
        "created_at": "2026-03-15T10:00:00Z",
        "updated_at": "2026-03-15T10:30:00Z",
        "message_count": 10
      }
    ],
    "total": 1
  }
}
```

### GET /api/conversations/{id}

获取会话详情。

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "conv_123",
    "title": "有限元分析讨论",
    "messages": [
      {
        "role": "user",
        "content": "请介绍一下有限元分析",
        "timestamp": "2026-03-15T10:00:00Z"
      },
      {
        "role": "assistant",
        "content": "有限元分析是一种...",
        "timestamp": "2026-03-15T10:00:05Z"
      }
    ]
  }
}
```

### DELETE /api/conversations/{id}

删除会话。

**响应**:

```json
{
  "success": true,
  "message": "会话已删除"
}
```

---

## 知识库 API

### POST /api/knowledge/search

搜索知识库。

**请求体**:

```json
{
  "query": "齿轮设计的基本原则",
  "top_k": 5,
  "mode": "hybrid",
  "rerank": true,
  "filters": {
    "category": "机械设计"
  }
}
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索查询 |
| `top_k` | integer | 否 | 返回数量，默认 5 |
| `mode` | string | 否 | 检索模式: vector/bm25/hybrid |
| `rerank` | boolean | 否 | 启用重排序 |
| `filters` | object | 否 | 过滤条件 |

**响应**:

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "doc_001",
        "content": "齿轮设计的基本原则包括...",
        "source": "机械设计/齿轮设计.md",
        "score": 0.95,
        "metadata": {
          "category": "机械设计",
          "title": "齿轮设计基础"
        }
      }
    ],
    "total": 1,
    "query_time": 0.15
  }
}
```

### POST /api/knowledge/documents

上传文档到知识库。

**请求体** (multipart/form-data):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 文档文件 |
| `category` | string | 否 | 分类名称 |
| `metadata` | json | 否 | 元数据 |

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "doc_002",
    "filename": "轴承选型指南.pdf",
    "category": "机械设计",
    "chunks": 15,
    "status": "indexed"
  }
}
```

### GET /api/knowledge/documents

获取文档列表。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `category` | string | 按分类筛选 |
| `page` | integer | 页码 |
| `limit` | integer | 每页数量 |

**响应**:

```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_001",
        "filename": "齿轮设计.md",
        "category": "机械设计",
        "chunks": 10,
        "created_at": "2026-03-15T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20
  }
}
```

### DELETE /api/knowledge/documents/{id}

删除文档。

**响应**:

```json
{
  "success": true,
  "message": "文档已删除"
}
```

### POST /api/knowledge/rebuild

重建知识库索引。

**响应**:

```json
{
  "success": true,
  "data": {
    "status": "processing",
    "job_id": "job_123"
  }
}
```

---

## 模型 API

### GET /api/models

获取可用模型列表。

**响应**:

```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "qwen2.5:3b",
        "name": "Qwen 2.5 3B",
        "provider": "ollama",
        "size": "2GB",
        "status": "available"
      },
      {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "status": "available"
      }
    ],
    "default": "qwen2.5:3b"
  }
}
```

### GET /api/models/current

获取当前使用的模型。

**响应**:

```json
{
  "success": true,
  "data": {
    "model": "qwen2.5:3b",
    "provider": "ollama"
  }
}
```

### POST /api/models/select

选择使用的模型。

**请求体**:

```json
{
  "model": "gpt-4",
  "provider": "openai"
}
```

**响应**:

```json
{
  "success": true,
  "message": "模型已切换"
}
```

---

## CAE API

### POST /api/cae/load

加载几何文件。

**请求体** (multipart/form-data):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 几何文件 (.step, .iges, .stl) |

**响应**:

```json
{
  "success": true,
  "data": {
    "id": "model_001",
    "filename": "bracket.step",
    "vertices": 1234,
    "faces": 567,
    "volume": 0.0015
  }
}
```

### POST /api/cae/mesh

生成网格。

**请求体**:

```json
{
  "model_id": "model_001",
  "mesh_size": 5.0,
  "algorithm": "Frontal-Delaunay",
  "order": 2
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "mesh_id": "mesh_001",
    "nodes": 5678,
    "elements": 3456,
    "element_type": "TET10"
  }
}
```

### POST /api/cae/solve

执行求解。

**请求体**:

```json
{
  "mesh_id": "mesh_001",
  "analysis_type": "static",
  "boundary_conditions": [
    {
      "type": "fixed",
      "faces": [1, 2]
    },
    {
      "type": "force",
      "face": 3,
      "value": [0, -1000, 0]
    }
  ],
  "material": {
    "youngs_modulus": 210000,
    "poissons_ratio": 0.3
  }
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "job_id": "job_001",
    "status": "running",
    "estimated_time": 60
  }
}
```

### GET /api/cae/results/{job_id}

获取求解结果。

**响应**:

```json
{
  "success": true,
  "data": {
    "job_id": "job_001",
    "status": "completed",
    "results": {
      "max_stress": 150.5,
      "max_displacement": 0.002,
      "min_safety_factor": 2.3
    },
    "files": {
      "vtk": "/api/cae/download/job_001/result.vtk",
      "frd": "/api/cae/download/job_001/result.frd"
    }
  }
}
```

---

## WebSocket API

### 连接

```javascript
const ws = new WebSocket('ws://localhost:8765/ws/chat');
```

### 消息格式

**发送消息**:

```json
{
  "type": "message",
  "content": "你好",
  "conversation_id": "conv_123"
}
```

**接收消息**:

```json
{
  "type": "chunk",
  "content": "你",
  "done": false
}
```

```json
{
  "type": "chunk",
  "content": "好",
  "done": true
}
```

### 消息类型

| 类型 | 方向 | 说明 |
|------|------|------|
| `message` | 客户端→服务器 | 发送消息 |
| `chunk` | 服务器→客户端 | 流式响应块 |
| `error` | 服务器→客户端 | 错误消息 |
| `ping` | 双向 | 心跳检测 |
| `pong` | 双向 | 心跳响应 |

### 心跳机制

```javascript
// 发送心跳
ws.send(JSON.stringify({ type: 'ping' }));

// 接收心跳响应
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'pong') {
    console.log('连接正常');
  }
};
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "模型不存在",
    "details": {
      "model": "unknown-model"
    }
  }
}
```

### 错误代码

| 代码 | HTTP 状态码 | 说明 |
|------|-------------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未认证 |
| `FORBIDDEN` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMITED` | 429 | 请求过于频繁 |
| `MODEL_NOT_FOUND` | 404 | 模型不存在 |
| `PROVIDER_ERROR` | 500 | 提供商错误 |
| `INTERNAL_ERROR` | 500 | 内部错误 |

### 错误处理示例

```python
import httpx

async def chat(message):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8765/api/chat',
            json={'message': message}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json()
            print(f"错误: {error['error']['message']}")
            raise Exception(error['error']['code'])
```

---

## SDK 示例

### Python SDK

```python
import httpx

class MechForgeClient:
    def __init__(self, base_url='http://localhost:8765'):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def chat(self, message, stream=False):
        response = await self.client.post(
            f'{self.base_url}/api/chat',
            json={'message': message, 'stream': stream}
        )
        return response.json()
    
    async def search_knowledge(self, query, top_k=5):
        response = await self.client.post(
            f'{self.base_url}/api/knowledge/search',
            json={'query': query, 'top_k': top_k}
        )
        return response.json()
    
    async def get_models(self):
        response = await self.client.get(
            f'{self.base_url}/api/models'
        )
        return response.json()

# 使用示例
async def main():
    client = MechForgeClient()
    
    # 对话
    result = await client.chat('你好')
    print(result['data']['message']['content'])
    
    # 知识库检索
    results = await client.search_knowledge('齿轮设计')
    for r in results['data']['results']:
        print(r['content'])
```

### JavaScript SDK

```javascript
class MechForgeClient {
  constructor(baseUrl = 'http://localhost:8765') {
    this.baseUrl = baseUrl;
  }
  
  async chat(message, options = {}) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, ...options })
    });
    return response.json();
  }
  
  async searchKnowledge(query, topK = 5) {
    const response = await fetch(`${this.baseUrl}/api/knowledge/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK })
    });
    return response.json();
  }
  
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`ws://${this.baseUrl.replace('http://', '')}/ws/chat`);
    ws.onmessage = (event) => onMessage(JSON.parse(event.data));
    return ws;
  }
}

// 使用示例
const client = new MechForgeClient();

// 对话
const result = await client.chat('你好');
console.log(result.data.message.content);

// WebSocket 流式对话
const ws = client.connectWebSocket((data) => {
  if (data.type === 'chunk') {
    process.stdout.write(data.content);
  }
});
ws.send(JSON.stringify({ type: 'message', content: '你好' }));
```

---

## 更多帮助

- [使用指南](USAGE.md)
- [配置说明](CONFIG.md)
- [架构文档](ARCHITECTURE.md)