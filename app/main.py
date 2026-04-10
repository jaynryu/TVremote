"""Apple TV Remote 데스크톱 앱 진입점."""

from app.async_bridge import AsyncBridge
from app.connection_manager import ConnectionManager
from app.ui.app_window import AppWindow


def main():
    bridge = AsyncBridge()
    bridge.start()

    manager = ConnectionManager()
    window = AppWindow(bridge, manager)
    window.mainloop()


if __name__ == "__main__":
    main()
