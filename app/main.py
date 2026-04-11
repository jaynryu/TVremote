"""Apple TV Remote 데스크톱 앱 진입점."""

import os
import webview

from app.async_bridge import AsyncBridge
from app.connection_manager import ConnectionManager
from app.api import Api


def main():
    bridge = AsyncBridge()
    bridge.start()

    manager = ConnectionManager()
    api = Api(bridge, manager)

    html_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")

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

    def on_closing():
        api.shutdown()

    window.events.closing += on_closing

    webview.start()


if __name__ == "__main__":
    main()
