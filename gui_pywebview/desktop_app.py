#!/usr/bin/env python3
"""
MechForge AI 桌面应用程序 - PyWebView 版本
使用 PyWebView 创建轻量级跨平台桌面应用
"""

import os
import sys
import threading
import time
import socket
import logging
from pathlib import Path
from typing import Optional

# ── 日志配置 ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("MechForge")

# ── 路径设置 ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
GUI_DIR = Path(__file__).parent.resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_resource_path(filename: str) -> Path:
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = GUI_DIR
    return base_path / filename


def find_free_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return start_port


# ── 后端服务器管理 ────────────────────────────────────────────────────────────
class BackendServer:
    """FastAPI 后端服务器管理"""

    def __init__(self, port: int = 5000):
        self.port = find_free_port(port)
        self.server_thread: Optional[threading.Thread] = None
        self.running = False

    def start(self) -> bool:
        """启动后端服务器"""
        logger.info(f"启动后端服务器 (端口: {self.port})...")

        def run_server():
            try:
                import uvicorn

                # 导入 FastAPI 应用
                from gui_pywebview.server import app

                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=self.port,
                    log_level="warning",
                    access_log=False,
                )
            except Exception as e:
                logger.error(f"服务器启动失败: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        if self._wait_for_server():
            self.running = True
            logger.info(f"后端服务器已启动: http://127.0.0.1:{self.port}")
            return True
        else:
            logger.error("后端服务器启动超时")
            return False

    def _wait_for_server(self, timeout: float = 30) -> bool:
        """等待服务器就绪"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", self.port))
                    return True
            except OSError:
                time.sleep(0.1)
        return False

    def stop(self):
        """停止服务器"""
        self.running = False
        logger.info("后端服务器已停止")


# ── PyWebView 窗口控制 API ────────────────────────────────────────────────────
class WindowAPI:
    """暴露给 JavaScript 的窗口控制 API"""

    def __init__(self):
        self._window = None
        self._is_fullscreen = False

    def set_window(self, window):
        """设置窗口引用"""
        self._window = window

    def minimize(self):
        """最小化窗口"""
        if self._window:
            self._window.minimize()
            logger.info("窗口已最小化")

    def maximize(self):
        """最大化窗口"""
        if self._window:
            self._window.maximize()
            logger.info("窗口已最大化")

    def restore(self):
        """还原窗口"""
        if self._window:
            self._window.restore()
            logger.info("窗口已还原")

    def toggle_fullscreen(self):
        """切换全屏/窗口模式"""
        if not self._window:
            return False
        if self._is_fullscreen:
            self._window.restore()
            self._is_fullscreen = False
            logger.info("退出全屏")
        else:
            self._window.maximize()
            self._is_fullscreen = True
            logger.info("进入全屏")
        return self._is_fullscreen

    def close(self):
        """关闭窗口"""
        if self._window:
            self._window.destroy()
            logger.info("窗口已关闭")

    def resize(self, width: int, height: int):
        """调整窗口大小"""
        if self._window:
            self._window.resize(width, height)

    def move(self, x: int, y: int):
        """移动窗口"""
        if self._window:
            self._window.move(x, y)


# ── PyWebView 应用 ────────────────────────────────────────────────────────────
class MechForgeApp:
    """MechForge AI 桌面应用"""

    def __init__(self, port: int = 5000):
        self.port = port
        self.backend: Optional[BackendServer] = None
        self.window = None
        self.window_api = WindowAPI()

    def create_window(self):
        """创建应用窗口"""
        import webview

        # 创建无边框窗口
        # frameless=True: 移除系统标题栏
        # 注意: Windows 上 transparent=True + frameless=True 有递归 bug
        # 通过 CSS 的 border-radius 和 box-shadow 实现圆角发光效果
        self.window = webview.create_window(
            title="MechForge AI v0.5.0",
            url=f"http://127.0.0.1:{self.port}",
            width=1200,
            height=800,
            min_size=(1000, 700),
            resizable=True,
            frameless=True,      # 移除系统标题栏
            easy_drag=True,      # 启用拖拽移动窗口（点击非交互区域）
            text_select=True,
            js_api=self.window_api,  # 暴露窗口控制 API 给 JavaScript
        )

        # 设置窗口图标
        icon_path = get_resource_path("dj-whale.png")
        if icon_path.exists():
            # PyWebView 会自动处理图标
            pass

        return self.window

    def on_loaded(self):
        """窗口加载完成回调 - 在此处设置窗口引用"""
        self.window_api.set_window(self.window)
        logger.info("窗口加载完成，API 已就绪")

    def on_closing(self):
        """窗口关闭回调"""
        logger.info("窗口正在关闭...")
        if self.backend:
            self.backend.stop()

    def run(self):
        """运行应用"""
        import webview

        print(
            """
╔════════════════════════════════════════════════════════════╗
║                    MechForge AI v0.5.0                     ║
║               PyWebView 轻量级桌面应用                       ║
╚════════════════════════════════════════════════════════════╝
        """
        )

        # 启动后端服务器
        self.port = find_free_port(self.port)
        self.backend = BackendServer(self.port)
        if not self.backend.start():
            print("[错误] 后端服务器启动失败")
            return
        self.port = self.backend.port

        # 创建窗口
        self.create_window()

        # 注册事件回调
        self.window.events.loaded += self.on_loaded
        self.window.events.closing += self.on_closing

        # 启动事件循环
        webview.start(debug=False, http_server=False)


def main():
    """主入口"""
    try:
        app = MechForgeApp()
        app.run()
    except ImportError as e:
        print(f"[错误] 缺少依赖: {e}")
        print("\n请安装依赖:")
        print("  pip install pywebview")
        input("\n按回车键退出...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback

        traceback.print_exc()
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()