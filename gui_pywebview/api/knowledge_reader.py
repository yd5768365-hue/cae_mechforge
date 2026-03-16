"""
知识阅读器 API
提供书籍列表、正文提取和问答功能
"""

import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .knowledge_engine import get_knowledge_engine

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Reader"])

# 知识库目录
KNOWLEDGE_DIR = get_knowledge_engine().knowledge_dir


# ── 书籍列表 ─────────────────────────────────────────────────────────────


@router.get("/list")
async def list_books() -> list[dict[str, Any]]:
    """返回已入库的书籍元数据列表（按标题去重）"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
    except Exception:
        return []

    if engine.doc_count == 0:
        return []

    try:
        results = engine._collection.get(include=["metadatas"])
        seen: dict[str, dict[str, Any]] = {}

        for meta in results.get("metadatas", []):
            title = meta.get("title", "未知")
            if not title or title == "未知":
                continue

            if title not in seen:
                seen[title] = {
                    "id": title.replace(" ", "_"),
                    "title": title,
                    "author": meta.get("author", ""),
                    "edition": meta.get("edition", ""),
                    "tags": meta.get("tags", []),
                    "chunks": 0,
                    "source": meta.get("source", ""),
                }
            seen[title]["chunks"] += 1

        books = list(seen.values())

        # 补充文件大小
        for book in books:
            source = book.get("source", "")
            if source:
                fp = Path(source)
                if fp.exists():
                    try:
                        size_mb = fp.stat().st_size / 1024 / 1024
                        book["size"] = f"{size_mb:.1f} MB"
                    except Exception:
                        pass

        return books

    except Exception as e:
        return []


# ── 书籍正文 ─────────────────────────────────────────────────────────────


@router.get("/book_content/{book_id}")
async def book_content(book_id: str) -> dict[str, Any]:
    """
    提取书籍全文，按标题行分割成章节。
    返回: { chapters: [...], content: "markdown text" }
    """
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识库未就绪: {e}")

    # 解析 book_id
    title = book_id.replace("_", " ").strip()

    # 从 ChromaDB 按书名拉取所有片段
    try:
        results = engine._collection.get(
            where={"title": title},
            include=["documents", "metadatas"],
        )
        docs = results.get("documents", [])

        if not docs:
            raise ValueError("no docs")

        # 按 chunk_index 排序后拼接
        metas = results.get("metadatas", [])
        indexed_docs = list(zip(metas, docs))
        indexed_docs.sort(key=lambda x: x[0].get("chunk_index", 0))
        full_text = "\n\n".join(doc for _, doc in indexed_docs)

    except Exception:
        # 回退：直接读原文件
        full_text = _extract_from_file(title)

    if not full_text:
        full_text = "暂无文本内容"

    # 提取章节标题
    chapter_pattern = re.compile(
        r"^(第[一二三四五六七八九十百\d]+[章节部篇]|Chapter\s+\d+|§\d+|\d+\.\s).+",
        re.MULTILINE,
    )
    chapters = [m.group(0).strip()[:50] for m in chapter_pattern.finditer(full_text)]
    if not chapters:
        chapters = ["全文"]

    # 转换章节标题为 Markdown 标题
    def upgrade_heading(text: str) -> str:
        def repl(m: re.Match) -> str:
            return f"## {m.group(0)}"

        return chapter_pattern.sub(repl, text)

    # 限制内容长度
    md_content = upgrade_heading(full_text[:50000])

    return {"chapters": chapters[:30], "content": md_content}


def _extract_from_file(title: str) -> str:
    """直接从原始文件提取文本"""
    # 尝试在知识库目录中找匹配文件
    for ext in [".pdf", ".txt", ".md"]:
        try:
            candidates = list(KNOWLEDGE_DIR.glob(f"*{ext}"))
            for fp in candidates:
                if title.lower() in fp.stem.lower():
                    if ext == ".pdf":
                        return _pdf_to_text(fp)
                    else:
                        return fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
    return ""


def _pdf_to_text(path: Path) -> str:
    """PDF 转文本"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        text = "\n\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    except ImportError:
        return "PDF 文本提取失败（未安装 PyMuPDF）"
    except Exception as e:
        return f"PDF 文本提取失败: {e}"


# ── 问书接口（SSE 流式） ─────────────────────────────────────────────


class AskBookRequest(BaseModel):
    book_id: str
    question: str
    history: list[dict[str, str]] = []


@router.post("/ask_book")
async def ask_book(req: AskBookRequest) -> StreamingResponse:
    """
    RAG 检索 + LLM 流式回答。
    使用 SSE 格式返回，前端逐 token 渲染。
    """
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识库未就绪: {e}")

    title = req.book_id.replace("_", " ").strip()

    # 1. 检索相关片段
    try:
        chunks = engine.search(req.question, top_k=5)
        # 过滤出这本书的内容
        context_parts = []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            if meta.get("title", "").lower() == title.lower():
                context_parts.append(chunk.get("content", ""))
        context = "\n\n---\n\n".join(context_parts) if context_parts else "（未找到本书相关内容）"
    except Exception as e:
        context = f"（检索失败: {e}）"

    # 2. 构造 System Prompt
    system_prompt = f"""你是《{title}》的专属阅读助手。
请严格基于书中内容回答问题，不要引入书外知识。
如书中没有相关内容，直接说明。回答简洁，专业，用中文。

【书中相关原文】
{context}"""

    # 3. 构造消息列表
    messages = []
    for h in req.history[-6:]:
        if "role" in h and "content" in h:
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": req.question})

    # 4. 流式返回
    async def generate():
        try:
            # 获取 LLM 客户端
            from .deps import get_llm_client
            import json

            llm = get_llm_client()
            full_response = ""

            for chunk in llm.provider.chat(messages, stream=True):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
