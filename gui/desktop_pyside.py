#!/usr/bin/env python3
"""
MechForge AI 桌面应用程序 - PySide6 版本
使用 PySide6 + QWebEngineView 创建独立窗口
"""

import os
import sys
import threading
import time
import socket
import logging
from pathlib import Path

# ── Intel 核显兼容性修复：禁用 GPU 加速 ─────────────────────
# 必须在 Qt 导入之前设置，解决 Intel UHD 核显与 WebEngineView 的闪烁问题
# 问题原因：QWebEngineView 基于 Chromium 需要 GPU 加速，但 Intel 核显 OpenGL 支持有限
# 解决方案：强制软件渲染，绕过 GPU 加速
os.environ["QT_OPENGL"] = "software"  # 使用软件 OpenGL 渲染
os.environ["QT_ANGLE_PLATFORM"] = "warp"  # Windows: 使用 WARP 软件渲染器
os.environ["QT_WEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu "  # 禁用 GPU 加速
    "--disable-gpu-rasterization "  # 禁用 GPU 光栅化
    "--disable-accelerated-2d-canvas "  # 禁用 2D 画布加速
    "--disable-es3-apis "  # 禁用 GLES3，回退到 GLES2
    "--disable-gpu-compositing"  # 禁用 GPU 合成
)

# ── 所有 Qt 导入统一放顶部，避免局部导入失效 ─────────────
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStatusBar
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtCore import QUrl, Qt, QSize
from PySide6.QtGui import QIcon, QFont

# ── 日志 ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("MechForge")

PROJECT_ROOT = Path(__file__).parent.resolve()


def find_free_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port


def get_resource_path(filename: str) -> Path:
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = PROJECT_ROOT
    return base_path / filename


# ── 后端服务器管理 ────────────────────────────────────────
class BackendServer:
    def __init__(self, port: int = 5000):
        self.port = find_free_port(port)
        self.server_thread = None
        self.running = False

    def start(self) -> bool:
        logger.info(f"启动后端服务器 (端口: {self.port})...")

        def run_server():
            try:
                import uvicorn
                server_path = get_resource_path("server.py")
                if server_path.exists():
                    if str(server_path.parent) not in sys.path:
                        sys.path.insert(0, str(server_path.parent))
                from server import app
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=self.port,
                    log_level="warning",
                    access_log=False
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
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('127.0.0.1', self.port))
                    return True
            except OSError:
                time.sleep(0.1)
        return False

    def stop(self):
        self.running = False
        logger.info("后端服务器已停止")


# ── 主窗口 ───────────────────────────────────────────────
class MainWindow:
    def __init__(self, port: int = 5000):
        self.port = port
        self.backend = None
        self.app = None
        self.window = None
        self.web_view = None

    def create_window(self):
        # 创建 QApplication - 启用软件 OpenGL 渲染
        # 必须在 QApplication 创建之前设置属性
        from PySide6.QtCore import QCoreApplication, Qt
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MechForge AI")
        self.app.setApplicationVersion("0.5.0")
        self.app.setStyle("Fusion")

        # 主窗口
        self.window = QMainWindow()
        self.window.setWindowTitle("MechForge AI v0.5.0")
        self.window.setMinimumSize(1000, 700)
        self.window.resize(1200, 800)

        # DWM 兼容性优化：减少窗口重绘冲突
        self.window.setAttribute(Qt.WidgetAttribute.WA_StaticContents)  # 避免不必要的重绘
        self.window.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)  # 优化绘制事件

        icon_path = get_resource_path("dj-whale.png")
        if icon_path.exists():
            self.window.setWindowIcon(QIcon(str(icon_path)))

        # 布局
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)

        # WebEngineView
        self.web_view = QWebEngineView()

        # 配置 WebEngine 设置 - 禁用 GPU 加速以解决 Intel 核显兼容性问题
        settings = self.web_view.page().settings()
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        # 禁用 GPU 加速相关功能（某些属性在旧版本 PySide6 中可能不存在）
        try:
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.AcceleratedVideoDecodeEnabled, False
            )
        except AttributeError:
            pass
        try:
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.WebGLEnabled, False
            )
        except AttributeError:
            pass

        url = f"http://127.0.0.1:{self.port}"
        logger.info(f"加载页面: {url}")
        self.web_view.setUrl(QUrl(url))
        layout.addWidget(self.web_view)

        # 状态栏
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0f172a;
                color: #94a3b8;
                border-top: 1px solid #1e293b;
                font-size: 12px;
                padding: 4px 8px;
            }
        """)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #22d3ee;")
        status_bar.addWidget(self.status_label)

        api_label = QLabel(f"API: http://127.0.0.1:{self.port}")
        api_label.setStyleSheet("color: #64748b; margin-left: 20px;")
        status_bar.addPermanentWidget(api_label)

        self.window.setStatusBar(status_bar)
        self.window.closeEvent = self._on_close

        return self.window

    def _create_title_bar(self) -> QWidget:
        """创建自定义标题栏"""
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-bottom: 1px solid #1e293b;
            }
        """)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(12, 0, 8, 0)

        logo_label = QLabel("⚙ MechForge AI")
        logo_label.setStyleSheet("""
            QLabel { color: #f8fafc; font-size: 14px; font-weight: bold; }
        """)
        layout.addWidget(logo_label)

        version_label = QLabel("v0.5.0")
        version_label.setStyleSheet("""
            QLabel { color: #64748b; font-size: 11px; margin-left: 8px; }
        """)
        layout.addWidget(version_label)

        layout.addStretch()

        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #22d3ee; font-size: 10px;")
        layout.addWidget(status_dot)

        status_text = QLabel("运行中")
        status_text.setStyleSheet("color: #94a3b8; font-size: 12px; margin-right: 16px;")
        layout.addWidget(status_text)

        return title_bar

    def _on_close(self, event):
        logger.info("窗口正在关闭...")
        if self.backend:
            self.backend.stop()
        event.accept()

    def run(self):
        print("""
╔════════════════════════════════════════════════════════════╗
║                    MechForge AI v0.5.0                     ║
║              PySide6 + QWebEngineView 桌面应用              ║
╚════════════════════════════════════════════════════════════╝
        """)

        # 自动查找可用端口
        self.port = find_free_port(self.port)
        self.backend = BackendServer(self.port)
        if not self.backend.start():
            print("[错误] 后端服务器启动失败")
            return
        self.port = self.backend.port

        self.create_window()
        self.window.show()
        logger.info("窗口已显示")
        sys.exit(self.app.exec())


def main():
    try:
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"[错误] 缺少依赖: {e}")
        print("\n请安装依赖:")
        print("  pip install PySide6")
        input("\n按回车键退出...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")


if __name__ == '__main__':
    main()