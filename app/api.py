"""pywebview에서 호출할 Python API 클래스."""

import webview
from app.connection_manager import ConnectionManager
from app.async_bridge import AsyncBridge


class Api:
    """JavaScript에서 window.pywebview.api.method()로 호출되는 메서드들."""

    def __init__(self, bridge: AsyncBridge, manager: ConnectionManager):
        self._bridge = bridge
        self._manager = manager
        self._window = None

    def set_window(self, window):
        self._window = window

    def scan_devices(self):
        future = self._bridge.run(self._manager.scan())
        try:
            devices = future.result(timeout=10)
            return {"devices": devices}
        except Exception as e:
            return {"error": str(e)}

    def connect(self, device_id):
        # 크레덴셜 없으면 페어링 필요
        if not self._manager.has_credentials(device_id):
            return {"needs_pairing": True}

        future = self._bridge.run(self._manager.connect(device_id))
        try:
            future.result(timeout=10)
            return {"status": "connected"}
        except Exception as e:
            return {"needs_pairing": True, "error": str(e)}

    def start_pairing(self, device_id):
        future = self._bridge.run(self._manager.start_pairing(device_id))
        try:
            result = future.result(timeout=10)
            return result
        except Exception as e:
            return {"error": str(e)}

    def finish_pairing(self, device_id, pin):
        future = self._bridge.run(self._manager.finish_pairing(device_id, pin))
        try:
            result = future.result(timeout=10)
            if result.get("paired"):
                # 페어링 성공 후 자동 연결
                connect_future = self._bridge.run(self._manager.connect(device_id))
                connect_future.result(timeout=10)
            return result
        except Exception as e:
            return {"error": str(e)}

    def send_command(self, command):
        future = self._bridge.run(self._manager.send_command(command))
        try:
            future.result(timeout=5)
            return {"status": "ok"}
        except Exception as e:
            return {"error": str(e)}

    def toggle_power(self):
        if self._manager.is_suspended:
            future = self._bridge.run(self._manager.wake())
        else:
            future = self._bridge.run(self._manager.send_command("control_center"))
        try:
            future.result(timeout=5)
            return {"status": "ok"}
        except Exception as e:
            return {"error": str(e)}

    def send_text(self, text):
        future = self._bridge.run(self._manager.send_text(text))
        try:
            future.result(timeout=5)
            return {"status": "ok"}
        except Exception as e:
            return {"error": str(e)}

    def get_status(self):
        future = self._bridge.run(self._manager.get_status())
        try:
            return future.result(timeout=5)
        except Exception as e:
            return {"error": str(e)}

    def disconnect(self):
        device_id = self._manager.connected_device_id
        if device_id:
            future = self._bridge.run(self._manager.disconnect(device_id))
            try:
                future.result(timeout=5)
            except Exception:
                pass
        return {"status": "disconnected"}

    def shutdown(self):
        future = self._bridge.run(self._manager.shutdown())
        try:
            future.result(timeout=3)
        except Exception:
            pass
        self._bridge.shutdown()

    def quit(self):
        """앱을 종료한다."""
        import os
        try:
            future = self._bridge.run(self._manager.shutdown())
            future.result(timeout=1)
        except Exception:
            pass
        self._bridge.shutdown()
        os._exit(0)
