#!/usr/bin/env python3
"""
MechForge AI 桌面应用程序 - 完整版
集成后端服务器 + 前端界面
"""

import os
import sys
import threading
import time
import webview
import subprocess
import socket
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("MechForge")

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_free_port(start_port=5000, max_attempts=100):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port


def get_resource_path(filename):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = PROJECT_ROOT
    return os.path.join(base_path, filename)


class BackendServer:
    """后端服务器管理"""

    def __init__(self, port=5000):
        self.port = find_free_port(port)
        self.process = None
        self.server_thread = None
        self.running = False

    def start(self):
        """启动后端服务器"""
        logger.info(f"启动后端服务器 (端口: {self.port})...")

        if getattr(sys, 'frozen', False):
            # 打包后：使用内嵌服务器
            self._start_embedded_server()
        else:
            # 开发模式：使用子进程
            self._start_subprocess_server()

        # 等待服务器启动
        self._wait_for_server()
        self.running = True
        logger.info(f"后端服务器已启动: http://127.0.0.1:{self.port}")

    def _start_embedded_server(self):
        """启动内嵌服务器（打包后使用）"""
        def run_server():
            import uvicorn
            from server import app

            # 配置日志级别
            log_config = uvicorn.config.LOGGING_CONFIG
            log_config["formatters"]["access"]["fmt"] = '%(levelprefix)s %(message)s'

            uvicorn.run(
                app,
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
                access_log=False
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def _start_subprocess_server(self):
        """启动子进程服务器（开发模式）"""
        server_script = os.path.join(PROJECT_ROOT, "server.py")

        self.process = subprocess.Popen(
            [sys.executable, server_script, "--port", str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=PROJECT_ROOT
        )

    def _wait_for_server(self, timeout=30):
        """等待服务器启动"""
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
        """停止后端服务器"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            logger.info("后端服务器已停止")


class DesktopApp:
    """桌面应用程序"""

    def __init__(self):
        self.window = None
        self.backend = None
        self.port = 5000

    def create_window(self):
        """创建桌面窗口"""
        # 等待后端启动
        if self.backend:
            time.sleep(1)

        # 创建窗口
        url = f"http://127.0.0.1:{self.port}"
        logger.info(f"打开窗口: {url}")

        self.window = webview.create_window(
            title='MechForge AI',
            url=url,
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            text_select=True,
            confirm_close=True
        )

        # 绑定事件
        self.window.events.closing += self.on_closing

        return self.window

    def on_closing(self):
        """窗口关闭回调"""
        logger.info("窗口正在关闭...")
        if self.backend:
            self.backend.stop()
        return True

    def run(self):
        """运行桌面应用"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                    MechForge AI v0.5.0                     ║
║                    桌面应用程序                             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)

        # 启动后端服务器
        self.backend = BackendServer(self.port)
        self.backend.start()
        self.port = self.backend.port

        # 创建窗口
        self.create_window()

        # 启动 WebView
        logger.info("启动桌面窗口...")
        webview.start(debug=False)

        logger.info("应用程序已退出")


def main():
    """主入口"""
    try:
        app = DesktopApp()
        app.run()
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")


if __name__ == '__main__':
    main()