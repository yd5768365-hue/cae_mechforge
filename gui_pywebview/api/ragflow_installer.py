"""
RAGFlow 安装向导 API 路由
"""

import asyncio
import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .state import state

router = APIRouter(prefix="/api/ragflow", tags=["RAGFlow"])

# 当前环境设置
_current_env = "windows"
_current_wsl_distro = ""


def _get_ragflow_url() -> str:
    """获取 RAGFlow URL"""
    try:
        if hasattr(state, "config") and hasattr(state.config, "knowledge"):
            config = state.config.knowledge
            if hasattr(config, "ragflow"):
                return config.ragflow.url or "http://localhost"
            elif isinstance(config, dict):
                return config.get("ragflow", {}).get("url", "http://localhost")
    except Exception:
        pass
    return "http://localhost"


def _run_docker_cmd(args: list[str], use_wsl: bool = False, distro: str = "") -> subprocess.CompletedProcess:
    """运行 docker 命令，支持 WSL"""
    if use_wsl and distro:
        # 使用 WSL 运行命令
        wsl_cmd = distro if distro != "default" else ""
        cmd = ["wsl"]
        if wsl_cmd:
            cmd.extend(["-d", wsl_cmd])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    else:
        # 直接运行
        return subprocess.run(args, capture_output=True, text=True, timeout=120)


# ── 0. 列出 WSL 发行版 ─────────────────────────────────────────────────


@router.get("/list_wsl")
async def list_wsl() -> dict[str, Any]:
    """列出已安装的 WSL 发行版"""
    try:
        result = subprocess.run(
            ["wsl", "--list", "--quiet"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            distros = [d.strip() for d in result.stdout.split("\n") if d.strip()]
            return {"distros": distros}
        return {"distros": [], "error": result.stderr}
    except Exception as e:
        return {"distros": [], "error": str(e)}


# ── 1. 检测 Docker ───────────────────────────────────────────────────────


@router.get("/check_docker")
async def check_docker(
    env: str = Query("windows", description="运行环境: windows 或 wsl"),
    distro: str = Query("", description="WSL 发行版"),
) -> dict[str, Any]:
    """检测 Docker 是否安装"""
    global _current_env, _current_wsl_distro
    _current_env = env
    _current_wsl_distro = distro

    use_wsl = env == "wsl"
    is_default = distro == "default" or not distro

    try:
        if use_wsl:
            # 检测 WSL 中的 Docker
            wsl_cmd = ["wsl"]
            if not is_default and distro:
                wsl_cmd.extend(["-d", distro])
            wsl_cmd.extend(["docker", "--version"])

            result = subprocess.run(
                wsl_cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = result.stdout.strip().replace("Docker version ", "")
                return {"installed": True, "version": version, "env": "wsl", "distro": distro}
            return {"installed": False, "version": None, "env": "wsl"}
        else:
            # Windows Docker
            if shutil.which("docker") is None:
                return {"installed": False, "version": None}
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version = result.stdout.strip().replace("Docker version ", "")
            return {"installed": True, "version": version, "env": "windows"}
    except Exception:
        return {"installed": False, "version": None, "env": env}


# ── 2. 检测端口 80 可用性 ───────────────────────────────────────────────


@router.get("/check_port")
async def check_port(
    env: str = Query("windows", description="运行环境"),
    distro: str = Query("", description="WSL 发行版"),
) -> dict[str, Any]:
    """检测端口 80 是否可用"""
    # WSL2 端口通过 localhost 访问
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("127.0.0.1", 80))
        s.close()
        return {"available": result != 0, "in_use": result == 0}
    except Exception:
        return {"available": False, "in_use": True}


# ── 3. 健康检查 ─────────────────────────────────────────────────────────


@router.get("/health")
async def health_check(
    env: str = Query("windows", description="运行环境"),
    distro: str = Query("", description="WSL 发行版"),
) -> dict[str, Any]:
    """检查 RAGFlow 服务健康状态"""
    # WSL2 中运行的服务通过 localhost 访问
    url = _get_ragflow_url()
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{url}/v1/health")
            return {"running": resp.status_code == 200}
    except Exception:
        return {"running": False}


# ── 4. 自动启动容器（流式输出日志） ─────────────────────────────────────


class StartRequest(BaseModel):
    env: str = "windows"
    distro: str = "default"


@router.post("/start")
async def start_ragflow(req: StartRequest) -> StreamingResponse:
    """流式返回 docker compose 启动日志"""
    use_wsl = req.env == "wsl"
    distro = req.distro if req.distro != "default" else ""
    is_default = not distro

    async def generate():
        clone_dir = Path.home() / "ragflow"
        env_prefix = f"[WSL:{distro}] " if use_wsl else "[Windows] "

        # 步骤 1：检查是否已 clone
        if not clone_dir.exists():
            yield json.dumps({"text": env_prefix + "正在 clone RAGFlow 仓库...", "pct": 15, "status": "克隆仓库中"}) + "\n"
            proc = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                "https://github.com/infiniflow/ragflow.git",
                str(clone_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            async for line in proc.stdout:
                yield json.dumps({"text": line.decode().rstrip()}) + "\n"
            await proc.wait()
        else:
            yield json.dumps({"text": env_prefix + "仓库已存在，跳过 clone", "pct": 15}) + "\n"

        # 步骤 2：docker compose up -d
        compose_dir = clone_dir / "docker"
        yield json.dumps({"text": env_prefix + "执行 docker compose up -d ...", "pct": 30, "status": "拉取镜像中"}) + "\n"

        # 根据环境构建命令
        if use_wsl:
            # WSL 中运行
            cmd = ["wsl"]
            if not is_default and distro:
                cmd.extend(["-d", distro])
            cmd.extend(["bash", "-c", f"cd /mnt/{compose_dir.drive.strip(':')}{compose_dir.path} && docker compose up -d"])
        else:
            # Windows 中运行
            cmd = ["docker", "compose", "up", "-d"]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        async for line in proc.stdout:
            text = line.decode().rstrip()
            pct = 80 if "Started" in text or "Running" in text else None
            result = {"text": env_prefix + text}
            if pct:
                result["pct"] = pct
            yield json.dumps(result) + "\n"

        rc = await proc.wait()
        if rc == 0:
            yield json.dumps({"text": "容器启动成功 ✓", "ok": True, "pct": 100, "status": "完成"}) + "\n"
        else:
            yield json.dumps({"text": f"启动失败，退出码 {rc}", "ok": False}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ── 5. 测试连接 + 保存配置 ───────────────────────────────────────────────


class ConnectRequest(BaseModel):
    url: str
    api_key: str
    dataset_id: str


@router.post("/test_connection")
async def test_connection(req: ConnectRequest) -> dict[str, Any]:
    """测试 RAGFlow 连接并保存配置"""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            # 验证 API Key：拉取知识库列表
            resp = await client.get(
                f"{req.url}/v1/dataset",
                headers={"Authorization": f"Bearer {req.api_key}"},
            )
            if resp.status_code == 401:
                return {"success": False, "message": "API Key 无效"}
            resp.raise_for_status()

            # 验证 Dataset ID：获取文档列表
            doc_resp = await client.get(
                f"{req.url}/v1/dataset/{req.dataset_id}/document",
                headers={"Authorization": f"Bearer {req.api_key}"},
            )
            if doc_resp.status_code == 404:
                return {"success": False, "message": "Dataset ID 不存在，请检查知识库 ID"}

            doc_count = doc_resp.json().get("data", {}).get("total", 0)

        # 保存到配置文件
        _save_ragflow_config(req.url, req.api_key, req.dataset_id)

        return {"success": True, "doc_count": doc_count}

    except httpx.ConnectError:
        return {"success": False, "message": f"无法连接到 {req.url}，请确认 RAGFlow 正在运行"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def _save_ragflow_config(url: str, api_key: str, dataset_id: str) -> None:
    """把 RAGFlow 配置写入 .env 文件"""
    import os

    # 尝试多种可能的配置文件路径
    possible_paths = [
        Path(".env"),
        Path(os.getcwd()) / ".env",
        Path(__file__).parent.parent / ".env",
    ]

    env_path = None
    for p in possible_paths:
        if p.exists():
            env_path = p
            break

    if env_path is None:
        # 在 gui_pywebview 目录下创建
        env_path = Path(__file__).parent.parent / ".env"

    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []

    updated = {
        "RAG_BACKEND": "ragflow",
        "RAGFLOW_URL": url,
        "RAGFLOW_API_KEY": api_key,
        "RAGFLOW_DATASET_ID": dataset_id,
    }

    new_lines = []
    keys_written = set()
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            if key in updated:
                new_lines.append(f"{key}={updated[key]}")
                keys_written.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for key, val in updated.items():
        if key not in keys_written:
            new_lines.append(f"{key}={val}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
