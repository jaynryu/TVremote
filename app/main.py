"""Apple TV Remote 데스크톱 앱 진입점."""

import os
import sys
import webview

from app.async_bridge import AsyncBridge
from app.connection_manager import ConnectionManager
from app.api import Api


def _get_resource_path(relative_path):
    """PyInstaller 번들과 개발 환경 모두에서 리소스 경로를 반환한다."""
    if getattr(sys, '_MEIPASS', None):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def main():
    bridge = AsyncBridge()
    bridge.start()

    manager = ConnectionManager()
    api = Api(bridge, manager)

    html_path = _get_resource_path(os.path.join("app", "ui", "index.html"))
    if not os.path.exists(html_path):
        html_path = _get_resource_path(os.path.join("ui", "index.html"))

    window = webview.create_window(
        "Apple TV Remote",
        url=html_path,
        js_api=api,
        width=400,
        height=720,
        min_size=(360, 600),
        background_color="#000000",
        frameless=True,
        easy_drag=True,
    )

    api.set_window(window)

    def on_closing():
        api.shutdown()

    window.events.closing += on_closing

    webview.start()


if __name__ == "__main__":
    main()
