"""기기 검색 및 선택 화면."""

import customtkinter as ctk
from .styles import *


class PairingDialog(ctk.CTkToplevel):
    """페어링 PIN 입력 다이얼로그."""

    def __init__(self, parent, device_id, bridge, manager, on_paired):
        super().__init__(parent)
        self.title("페어링")
        self.geometry("320x280")
        self.resizable(False, False)
        self.configure(fg_color=BG_PRIMARY)
        self.grab_set()

        self._device_id = device_id
        self._bridge = bridge
        self._manager = manager
        self._on_paired = on_paired

        self._status_label = ctk.CTkLabel(
            self, text="페어링을 시작합니다...",
            font=(FONT_FAMILY, 15), text_color=TEXT_PRIMARY,
        )
        self._status_label.pack(pady=(24, 16))

        self._pin_entry = ctk.CTkEntry(
            self, placeholder_text="PIN 입력",
            font=(FONT_FAMILY, 20), width=200, height=44,
            fg_color=BG_SECONDARY, border_color=BG_TERTIARY,
            text_color=TEXT_PRIMARY, justify="center",
        )
        self._pin_entry.pack(pady=8)
        self._pin_entry.bind("<Return>", lambda e: self._submit_pin())

        self._submit_btn = ctk.CTkButton(
            self, text="확인", font=(FONT_FAMILY, 15, "bold"),
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_ACTIVE,
            width=200, height=40, command=self._submit_pin,
        )
        self._submit_btn.pack(pady=8)

        self._error_label = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 13),
            text_color=DANGER_RED,
        )
        self._error_label.pack(pady=4)

        self._start_pairing()

    def _start_pairing(self):
        self._bridge.run_with_callback(
            self._manager.start_pairing(self._device_id),
            root=self,
            on_success=self._on_pairing_started,
            on_error=self._on_pairing_error,
        )

    def _on_pairing_started(self, result):
        self._status_label.configure(text=result["message"])
        self._pin_entry.focus()

    def _on_pairing_error(self, error):
        self._error_label.configure(text=f"페어링 시작 실패: {error}")

    def _submit_pin(self):
        pin = self._pin_entry.get().strip()
        if not pin:
            return
        self._submit_btn.configure(state="disabled", text="처리 중...")

        self._bridge.run_with_callback(
            self._manager.finish_pairing(self._device_id, pin),
            root=self,
            on_success=self._on_pairing_finished,
            on_error=self._on_finish_error,
        )

    def _on_pairing_finished(self, result):
        if result.get("paired"):
            self._on_paired(self._device_id)
            self.destroy()
        else:
            self._error_label.configure(text="페어링에 실패했습니다.")
            self._submit_btn.configure(state="normal", text="확인")

    def _on_finish_error(self, error):
        self._error_label.configure(text=str(error))
        self._submit_btn.configure(state="normal", text="확인")


class DeviceListFrame(ctk.CTkFrame):
    """기기 검색 및 선택 프레임."""

    def __init__(self, parent, bridge, manager, on_connected):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self._bridge = bridge
        self._manager = manager
        self._on_connected = on_connected
        self._devices = []

        # 타이틀
        ctk.CTkLabel(
            self, text="Apple TV Remote",
            font=(FONT_FAMILY, 22, "bold"), text_color=TEXT_PRIMARY,
        ).pack(pady=(60, 24))

        # 기기 목록 스크롤
        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG_PRIMARY, width=320, height=300,
        )
        self._list_frame.pack(padx=24, fill="x")

        self._status_label = ctk.CTkLabel(
            self._list_frame, text="",
            font=(FONT_FAMILY, 14), text_color=TEXT_SECONDARY,
        )

        # 검색 버튼
        self._scan_btn = ctk.CTkButton(
            self, text="기기 검색", font=(FONT_FAMILY, 16, "bold"),
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_ACTIVE,
            width=200, height=44, corner_radius=12,
            command=self._scan,
        )
        self._scan_btn.pack(pady=(16, 0))

        # 에러 표시
        self._error_label = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 13),
            text_color=DANGER_RED,
        )
        self._error_label.pack(pady=8)

        # 초기 검색
        self.after(500, self._scan)

    def _scan(self):
        self._scan_btn.configure(state="disabled", text="검색 중...")
        self._error_label.configure(text="")
        self._clear_list()

        self._bridge.run_with_callback(
            self._manager.scan(),
            root=self,
            on_success=self._on_scan_complete,
            on_error=self._on_scan_error,
        )

    def _clear_list(self):
        for widget in self._list_frame.winfo_children():
            widget.destroy()

    def _on_scan_complete(self, devices):
        self._scan_btn.configure(state="normal", text="기기 검색")
        self._devices = devices
        self._clear_list()

        if not devices:
            ctk.CTkLabel(
                self._list_frame, text="기기를 찾지 못했습니다",
                font=(FONT_FAMILY, 14), text_color=TEXT_SECONDARY,
            ).pack(pady=20)
            return

        for device in devices:
            btn = ctk.CTkButton(
                self._list_frame, text="",
                fg_color=BG_SECONDARY, hover_color=BG_TERTIARY,
                height=60, corner_radius=12, anchor="w",
                command=lambda d=device: self._connect_device(d),
            )
            # 기기 이름 + 주소 표시
            name_label = ctk.CTkLabel(
                btn, text=device["name"],
                font=(FONT_FAMILY, 16), text_color=TEXT_PRIMARY,
                anchor="w",
            )
            name_label.place(x=18, y=10)
            name_label.bind("<Button-1>", lambda e, d=device: self._connect_device(d))

            addr_label = ctk.CTkLabel(
                btn, text=device["address"],
                font=(FONT_FAMILY, 12), text_color=TEXT_SECONDARY,
                anchor="w",
            )
            addr_label.place(x=18, y=34)
            addr_label.bind("<Button-1>", lambda e, d=device: self._connect_device(d))

            btn.pack(fill="x", pady=4)

    def _on_scan_error(self, error):
        self._scan_btn.configure(state="normal", text="기기 검색")
        self._error_label.configure(text=f"검색 실패: {error}")

    def _connect_device(self, device):
        self._error_label.configure(text="")
        self._scan_btn.configure(state="disabled", text="연결 중...")

        self._bridge.run_with_callback(
            self._manager.connect(device["id"]),
            root=self,
            on_success=lambda r: self._on_connect_success(device),
            on_error=lambda e: self._on_connect_error(device, e),
        )

    def _on_connect_success(self, device):
        self._scan_btn.configure(state="normal", text="기기 검색")
        self._on_connected(device)

    def _on_connect_error(self, device, error):
        self._scan_btn.configure(state="normal", text="기기 검색")
        # 페어링이 필요할 수 있음
        PairingDialog(
            self.winfo_toplevel(), device["id"],
            self._bridge, self._manager,
            on_paired=lambda did: self._after_pairing(device),
        )

    def _after_pairing(self, device):
        """페어링 후 연결 시도."""
        self._bridge.run_with_callback(
            self._manager.connect(device["id"]),
            root=self,
            on_success=lambda r: self._on_connected(device),
            on_error=lambda e: self._error_label.configure(text=f"연결 실패: {e}"),
        )
