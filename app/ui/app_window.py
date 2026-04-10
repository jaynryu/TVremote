"""메인 애플리케이션 윈도우."""

import customtkinter as ctk
from .styles import *
from .device_list_frame import DeviceListFrame
from .remote_frame import RemoteFrame


class AppWindow(ctk.CTk):
    """Apple TV Remote 메인 윈도우."""

    def __init__(self, bridge, manager):
        super().__init__()
        self._bridge = bridge
        self._manager = manager

        self.title("Apple TV Remote")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(360, 600)
        self.configure(fg_color=BG_PRIMARY)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 프레임
        self._device_frame = DeviceListFrame(
            self, bridge, manager, on_connected=self._show_remote,
        )
        self._remote_frame = RemoteFrame(
            self, bridge, manager, on_disconnected=self._show_device_list,
        )

        self._device_frame.pack(fill="both", expand=True)

        # 키보드 단축키
        self.bind("<KeyPress>", self._on_key)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_remote(self, device):
        self._device_frame.pack_forget()
        self._remote_frame.pack(fill="both", expand=True)
        self._remote_frame.set_device(device)

    def _show_device_list(self):
        self._remote_frame.pack_forget()
        self._device_frame.pack(fill="both", expand=True)

    def _on_key(self, event):
        # 텍스트 입력 중이면 무시
        focused = self.focus_get()
        if isinstance(focused, (ctk.CTkEntry,)):
            return

        if not self._manager.connected_device_id:
            return

        key_map = {
            "Up": "up",
            "Down": "down",
            "Left": "left",
            "Right": "right",
            "Return": "select",
            "Escape": "menu",
            "BackSpace": "menu",
            "space": "play_pause",
        }

        command = key_map.get(event.keysym)
        if command:
            self._bridge.run_with_callback(
                self._manager.send_command(command),
                root=self,
            )

    def _on_close(self):
        self._remote_frame.stop_refresh()
        self._bridge.run(self._manager.shutdown())
        self._bridge.shutdown()
        self.destroy()
