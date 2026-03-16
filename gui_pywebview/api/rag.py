"""
RAG API 路由 — 知识库向量检索与文档管理
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .knowledge_engine import get_knowledge_engine
from .state import state

logger = logging.getLogger("mechforge.api.rag")

router = APIRouter(prefix="/api/rag", tags=["RAG"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=20)


# ── 搜索端点 ──────────────────────────────────────────────────────────────────


@router.post("/search")
async def rag_search(request: RAGSearchRequest) -> dict:
    """语义搜索知识库"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
    except Exception as e:
        logger.warning("知识库引擎未就绪: %s", e)
        return {"results": [], "message": "知识库引擎未就绪"}

    if engine.doc_count == 0:
        return {"results": [], "message": "知识库为空，请先添加文档"}

    try:
        results = engine.search(request.query, top_k=request.limit)
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error("RAG 检索失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def rag_status() -> dict:
    """获取知识库状态"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
        stats = engine.get_stats()
        return {
            "enabled": state.config.knowledge.rag.enabled,
            "available": engine.is_ready,
            "doc_count": stats["doc_count"],
            "indexed_files": stats["indexed_files"],
            "knowledge_dir": stats["knowledge_dir"],
        }
    except Exception:
        return {
            "enabled": state.config.knowledge.rag.enabled,
            "available": False,
            "doc_count": 0,
            "indexed_files": 0,
            "knowledge_dir": str(engine.knowledge_dir),
        }


@router.post("/toggle")
async def toggle_rag(body: dict[str, Any]) -> dict:
    """切换 RAG 开关"""
    enabled = bool(body.get("enabled", False))
    state.config.knowledge.rag.enabled = enabled
    logger.info("RAG %s", "enabled" if enabled else "disabled")
    return {"success": True, "enabled": enabled}


# ── 文档管理端点 ──────────────────────────────────────────────────────────────


@router.post("/index")
async def index_documents(body: dict[str, Any] | None = None) -> dict:
    """索引知识库目录下的文档"""
    engine = get_knowledge_engine()
    directory = body.get("directory") if body else None

    try:
        result = engine.index_directory(directory)
        return result
    except Exception as e:
        logger.error("文档索引失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sources")
async def list_sources() -> dict:
    """列出已索引的文档源"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
        sources = engine.list_sources()
        return {"sources": sources, "total": len(sources)}
    except Exception as e:
        logger.error("获取文档源失败: %s", e)
        return {"sources": [], "total": 0}


@router.delete("/clear")
async def clear_knowledge() -> dict:
    """清空知识库"""
    engine = get_knowledge_engine()
    try:
        engine._ensure_ready()
        return engine.clear()
    except Exception as e:
        logger.error("清空知识库失败: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats")
async def knowledge_stats() -> dict:
    """获取知识库统计"""
    engine = get_knowledge_engine()
    try:
        engine._ensure_ready()
        return engine.get_stats()
    except Exception as e:
        return {"ready": False, "error": str(e)}


# ── 书籍管理端点 ──────────────────────────────────────────────────────────────


import json
import shutil
from pathlib import Path
from fastapi import UploadFile, File, Form

from .knowledge_engine import get_knowledge_engine, _file_hash, _read_file, _chunk_text

BOOKS_DIR = Path("data/books")
BOOKS_DIR.mkdir(parents=True, exist_ok=True)


# ── RAGFlow Provider ─────────────────────────────────────────────────────────


class RAGFlowProvider:
    """封装 RAGFlow REST API"""

    def __init__(self, base_url: str, api_key: str, kb_id: str):
        self.base = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.kb_id = kb_id
        self._doc_status_cache: dict[str, str] = {}

    async def add_book(self, file_path: Path, metadata: dict) -> dict:
        """上传并解析文档"""
        import httpx

        async with httpx.AsyncClient(timeout=180.0) as client:
            # 1. 上传文件
            with file_path.open("rb") as f:
                upload_resp = await client.post(
                    f"{self.base}/v1/dataset/{self.kb_id}/document",
                    headers={"Authorization": self.headers["Authorization"]},
                    files={"file": (file_path.name, f, "application/pdf")},
                    data={
                        "name": metadata.get("title", file_path.stem),
                        "parser_id": "naive",
                    },
                )
            upload_resp.raise_for_status()
            doc_id = upload_resp.json()["data"]["id"]

            # 2. 触发解析（异步）
            parse_resp = await client.post(
                f"{self.base}/v1/dataset/{self.kb_id}/document/run",
                headers=self.headers,
                json={"document_ids": [doc_id]},
            )
            parse_resp.raise_for_status()

            self._doc_status_cache[doc_id] = "RUNNING"
            logger.info("RAGFlow 文档上传成功, doc_id: %s", doc_id)

            return {"doc_id": doc_id, "status": "parsing"}

    async def get_parse_status(self, doc_id: str) -> str:
        """查询解析状态"""
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{self.base}/v1/dataset/{self.kb_id}/document",
                    headers=self.headers,
                    params={"id": doc_id},
                )
                docs = resp.json()["data"]["docs"]
                if docs:
                    status = docs[0].get("run", "UNKNOWN")
                    self._doc_status_cache[doc_id] = status
                    return status
            except Exception as e:
                logger.warning("查询 RAGFlow 解析状态失败: %s", e)
            return self._doc_status_cache.get(doc_id, "UNKNOWN")


def get_ragflow_provider() -> RAGFlowProvider | None:
    """获取 RAGFlow Provider 实例"""
    try:
        config = state.config
        # 尝试从 config.knowledge.ragflow 获取配置
        if hasattr(config, "knowledge") and hasattr(config.knowledge, "ragflow"):
            ragflow_config = config.knowledge.ragflow
            url = ragflow_config.url or "http://localhost:9380"
            api_key = ragflow_config.api_key or ""
            kb_id = ragflow_config.kb_id or ""
        else:
            # 兼容旧配置格式
            knowledge_config = getattr(config, "knowledge", {})
            ragflow_config = knowledge_config.get("ragflow", {}) if isinstance(knowledge_config, dict) else {}
            url = ragflow_config.get("url", "http://localhost:9380")
            api_key = ragflow_config.get("api_key", "")
            kb_id = ragflow_config.get("kb_id", "")

        if not api_key or not kb_id:
            logger.warning("RAGFlow 未配置 (api_key 或 kb_id 为空)")
            return None

        return RAGFlowProvider(base_url=url, api_key=api_key, kb_id=kb_id)
    except Exception as e:
        logger.warning("获取 RAGFlow 配置失败: %s", e)
        return None


@router.post("/add_book")
async def add_book(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(""),
    edition: str = Form(""),
    tags: str = Form("[]"),
    backend: str = Form("local"),
) -> dict:
    """添加书籍到知识库"""
    # 检查格式
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(400, detail="不支持的文件格式")

    # 保存文件
    safe_filename = Path(file.filename or "unknown").name
    save_path = BOOKS_DIR / safe_filename
    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # 解析元数据
    try:
        tags_list = json.loads(tags) if tags else []
    except json.JSONDecodeError:
        tags_list = []

    metadata = {
        "title": title,
        "author": author,
        "edition": edition,
        "tags": tags_list,
        "filename": safe_filename,
    }

    # 如果选择 RAGFlow 后端
    if backend == "ragflow":
        provider = get_ragflow_provider()
        if not provider:
            save_path.unlink(missing_ok=True)
            raise HTTPException(400, detail="RAGFlow 未配置，请在设置中配置 RAGFlow API Key 和 Knowledge ID")

        try:
            result = await provider.add_book(save_path, metadata)
            logger.info("RAGFlow 书籍上传成功: %s", title)
            return {
                "success": True,
                "message": "文件已上传到 RAGFlow，等待解析",
                "title": title,
                "doc_id": result.get("doc_id"),
            }
        except Exception as e:
            save_path.unlink(missing_ok=True)
            logger.error("RAGFlow 上传失败: %s", e, exc_info=True)
            raise HTTPException(500, detail=f"RAGFlow 上传失败: {str(e)}")

    # 默认使用本地 ChromaDB
    try:
        engine = get_knowledge_engine()
        engine._ensure_ready()

        # 读取文件
        text = _read_file(save_path)
        if not text or len(text.strip()) < 50:
            save_path.unlink(missing_ok=True)
            raise HTTPException(400, detail="文件内容过少，无法索引")

        # 切片
        chunks = _chunk_text(text)
        if not chunks:
            save_path.unlink(missing_ok=True)
            raise HTTPException(400, detail="无法分割文件内容")

        # 生成 hash
        fhash = _file_hash(save_path)

        # 移除旧文档（如果存在）
        engine._remove_file_docs(str(save_path))

        # 添加新文档
        ids = [f"{save_path.stem}_{i}_{fhash[:8]}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": title,
                "file_path": str(save_path.resolve()),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "title": title,
                "author": author,
                "edition": edition,
                "tags": tags_list,
            }
            for i in range(len(chunks))
        ]

        batch_size = 50
        for start in range(0, len(chunks), batch_size):
            end = min(start + batch_size, len(chunks))
            engine._collection.add(
                ids=ids[start:end],
                documents=chunks[start:end],
                metadatas=metadatas[start:end],
            )

        logger.info("已添加书籍: %s (%d 块)", title, len(chunks))

        return {
            "success": True,
            "message": f"成功入库 {len(chunks)} 个片段",
            "title": title,
        }

    except HTTPException:
        raise
    except Exception as e:
        save_path.unlink(missing_ok=True)
        logger.error("添加书籍失败: %s", e, exc_info=True)
        raise HTTPException(500, detail=f"RAG 入库失败: {str(e)}")


@router.get("/parse_status/{doc_id}")
async def parse_status(doc_id: str) -> dict:
    """查询 RAGFlow 文档解析状态"""
    provider = get_ragflow_provider()
    if not provider:
        return {"status": "unknown", "done": True, "message": "RAGFlow 未配置"}

    try:
        status = await provider.get_parse_status(doc_id)
        return {
            "status": status,
            "done": status == "DONE",
            "message": f"解析状态: {status}",
        }
    except Exception as e:
        logger.error("查询解析状态失败: %s", e)
        return {"status": "error", "done": False, "message": str(e)}
