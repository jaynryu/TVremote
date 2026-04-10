"""리모트 컨트롤 화면."""

import customtkinter as ctk
from .styles import *


class RemoteFrame(ctk.CTkFrame):
    """Apple TV 리모트 컨트롤 프레임."""

    def __init__(self, parent, bridge, manager, on_disconnected):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self._bridge = bridge
        self._manager = manager
        self._on_disconnected = on_disconnected
        self._status_timer = None
        self._keyboard_visible = False

        self._build_ui()

    def _build_ui(self):
        # 상단 헤더
        header = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        header.pack(fill="x", padx=20, pady=(16, 0))

        self._device_name_label = ctk.CTkLabel(
            header, text="", font=(FONT_FAMILY, 17, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self._device_name_label.pack()

        self._status_label = ctk.CTkLabel(
            header, text="", font=(FONT_FAMILY, 13),
            text_color=TEXT_SECONDARY,
        )
        self._status_label.pack(pady=(4, 0))

        # D-pad 영역
        dpad_frame = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        dpad_frame.pack(expand=True, fill="both")

        dpad = ctk.CTkFrame(dpad_frame, fg_color=BG_PRIMARY)
        dpad.place(relx=0.5, rely=0.5, anchor="center")

        btn_size = 72
        btn_radius = 18
        gap = 8

        # 위
        self._make_dpad_btn(dpad, "▲", "up", btn_size, btn_radius).grid(
            row=0, column=1, padx=gap, pady=gap
        )
        # 왼쪽
        self._make_dpad_btn(dpad, "◀", "left", btn_size, btn_radius).grid(
            row=1, column=0, padx=gap, pady=gap
        )
        # OK
        ok_btn = ctk.CTkButton(
            dpad, text="OK", width=80, height=80, corner_radius=40,
            font=(FONT_FAMILY, 18, "bold"),
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_ACTIVE,
            command=lambda: self._send("select"),
        )
        ok_btn.grid(row=1, column=1, padx=gap, pady=gap)
        # 오른쪽
        self._make_dpad_btn(dpad, "▶", "right", btn_size, btn_radius).grid(
            row=1, column=2, padx=gap, pady=gap
        )
        # 아래
        self._make_dpad_btn(dpad, "▼", "down", btn_size, btn_radius).grid(
            row=2, column=1, padx=gap, pady=gap
        )

        # 하단 버튼 영역
        buttons_frame = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 재생 컨트롤
        playback_row = ctk.CTkFrame(buttons_frame, fg_color=BG_PRIMARY)
        playback_row.pack(pady=(0, 14))

        self._make_ctrl_btn(playback_row, "⏮\n이전", "previous").pack(side="left", padx=8)
        self._make_ctrl_btn(playback_row, "⏯\n재생", "play_pause").pack(side="left", padx=8)
        self._make_ctrl_btn(playback_row, "⏭\n다음", "next").pack(side="left", padx=8)

        # 네비게이션 + 볼륨
        nav_row = ctk.CTkFrame(buttons_frame, fg_color=BG_PRIMARY)
        nav_row.pack(pady=(0, 14))

        self._make_ctrl_btn(nav_row, "☰\n메뉴", "menu").pack(side="left", padx=6)
        self._make_ctrl_btn(nav_row, "⌂\n홈", "home").pack(side="left", padx=6)
        self._make_ctrl_btn(nav_row, "🔉\n볼륨-", "volume_down").pack(side="left", padx=6)
        self._make_ctrl_btn(nav_row, "🔊\n볼륨+", "volume_up").pack(side="left", padx=6)

        power_btn = ctk.CTkButton(
            nav_row, text="⏻\n전원", width=64, height=56, corner_radius=14,
            font=(FONT_FAMILY, 14), fg_color=BG_SECONDARY, hover_color=BG_ACTIVE,
            text_color=DANGER_RED, command=self._toggle_power,
        )
        power_btn.pack(side="left", padx=6)

        # 키보드 바
        self._kb_frame = ctk.CTkFrame(buttons_frame, fg_color=BG_PRIMARY)

        self._kb_entry = ctk.CTkEntry(
            self._kb_frame, placeholder_text="텍스트 입력",
            font=(FONT_FAMILY, 16), height=40,
            fg_color=BG_SECONDARY, border_color=BG_TERTIARY,
            text_color=TEXT_PRIMARY,
        )
        self._kb_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._kb_entry.bind("<Return>", lambda e: self._send_text())

        kb_send_btn = ctk.CTkButton(
            self._kb_frame, text="전송", width=60, height=40,
            font=(FONT_FAMILY, 14, "bold"), corner_radius=10,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_ACTIVE,
            command=self._send_text,
        )
        kb_send_btn.pack(side="right")

        # 키보드 토글 버튼
        kb_toggle_row = ctk.CTkFrame(buttons_frame, fg_color=BG_PRIMARY)
        kb_toggle_row.pack(pady=(0, 8))

        ctk.CTkButton(
            kb_toggle_row, text="⌨️ 키보드", width=144, height=56, corner_radius=14,
            font=(FONT_FAMILY, 14), fg_color=BG_SECONDARY, hover_color=BG_ACTIVE,
            text_color=TEXT_PRIMARY, command=self._toggle_keyboard,
        ).pack()

        # 연결 해제
        ctk.CTkButton(
            buttons_frame, text="연결 해제",
            font=(FONT_FAMILY, 13), fg_color="transparent",
            hover_color=BG_SECONDARY, text_color=DANGER_RED,
            width=100, height=32, command=self._disconnect,
        ).pack(pady=(4, 0))

    def _make_dpad_btn(self, parent, text, command, size, radius):
        return ctk.CTkButton(
            parent, text=text, width=size, height=size, corner_radius=radius,
            font=(FONT_FAMILY, 24), fg_color=BG_SECONDARY, hover_color=BG_ACTIVE,
            text_color=TEXT_PRIMARY, command=lambda: self._send(command),
        )

    def _make_ctrl_btn(self, parent, text, command):
        return ctk.CTkButton(
            parent, text=text, width=64, height=56, corner_radius=14,
            font=(FONT_FAMILY, 14), fg_color=BG_SECONDARY, hover_color=BG_ACTIVE,
            text_color=TEXT_PRIMARY, command=lambda: self._send(command),
        )

    def set_device(self, device):
        """연결된 기기 정보를 설정하고 상태 갱신을 시작한다."""
        self._device_name_label.configure(text=device["name"])
        self._start_status_refresh()

    def _send(self, command):
        self._bridge.run_with_callback(
            self._manager.send_command(command),
            root=self,
        )

    def _toggle_power(self):
        self._bridge.run_with_callback(
            self._manager.toggle_power(),
            root=self,
        )

    def _toggle_keyboard(self):
        self._keyboard_visible = not self._keyboard_visible
        if self._keyboard_visible:
            self._kb_frame.pack(fill="x", pady=(0, 8))
            self._kb_entry.focus()
        else:
            self._kb_frame.pack_forget()

    def _send_text(self):
        text = self._kb_entry.get().strip()
        if not text:
            return
        self._bridge.run_with_callback(
            self._manager.send_text(text),
            root=self,
            on_success=lambda r: self._kb_entry.delete(0, "end"),
        )

    def _start_status_refresh(self):
        self._refresh_status()

    def _refresh_status(self):
        self._bridge.run_with_callback(
            self._manager.get_status(),
            root=self,
            on_success=self._update_status,
        )
        self._status_timer = self.after(5000, self._refresh_status)

    def _update_status(self, status):
        text = ""
        if status.get("title"):
            text = status["title"]
        if status.get("artist"):
            text += f" - {status['artist']}"
        if not text and status.get("app"):
            text = status["app"]
        self._status_label.configure(text=text)

    def _disconnect(self):
        if self._status_timer:
            self.after_cancel(self._status_timer)
            self._status_timer = None

        device_id = self._manager.connected_device_id
        if device_id:
            self._bridge.run_with_callback(
                self._manager.disconnect(device_id),
                root=self,
            )
        self._keyboard_visible = False
        self._kb_frame.pack_forget()
        self._status_label.configure(text="")
        self._on_disconnected()

    def stop_refresh(self):
        if self._status_timer:
            self.after_cancel(self._status_timer)
            self._status_timer = None
