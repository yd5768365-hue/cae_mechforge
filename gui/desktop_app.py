#!/usr/bin/env python3
"""
MechForge AI 桌面应用程序
使用 PyWebView 将 GUI 打包成独立的桌面应用
"""

import os
import sys
import webview

# 添加当前目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


class DesktopApp:
    """桌面应用程序类"""

    def __init__(self):
        self.window = None

    def create_window(self):
        """创建桌面窗口 - 直接打开本地 HTML 文件"""
        # 获取 index.html 的绝对路径
        html_path = os.path.join(PROJECT_ROOT, 'index.html')
        # 转换为 file:// URL
        url = f"file:///{html_path.replace(os.sep, '/')}"
        print(f"[Desktop] 打开文件: {url}")

        # 创建窗口 - pywebview 6.x 兼容
        self.window = webview.create_window(
            title='MechForge AI',
            url=url,
            width=1200,
            height=800,
            resizable=True
        )

        return self.window

    def on_closing(self, window, event=None):
        """窗口关闭时的回调"""
        print("[Desktop] 窗口正在关闭...")
        return True  # 允许关闭

    def run(self):
        """运行桌面应用程序"""
        # 创建桌面窗口
        window = self.create_window()

        # 设置关闭回调 (pywebview 6.x 兼容方式)
        try:
            window.events.closing += self.on_closing
        except Exception as e:
            print(f"[Desktop] 设置关闭回调失败: {e}")

        # 显示窗口（阻塞直到窗口关闭）
        print("[Desktop] 正在启动桌面窗口...")
        webview.start(debug=False)

        print("[Desktop] 应用程序已退出")


def get_resource_path(filename):
    """获取资源文件的路径（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)


def main():
    """主入口点"""
    print("""
============================================================
                  MechForge AI v0.5.0
                   桌面应用程序
============================================================
    """)

    app = DesktopApp()
    app.run()


if __name__ == '__main__':
    main()
