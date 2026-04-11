"""Apple TV 연결을 관리하는 클래스."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import pyatv
from pyatv.const import InputAction, PowerState
from pyatv.interface import AppleTV

CREDENTIALS_DIR = Path.home() / "Library" / "Application Support" / "TVRemote"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

VALID_COMMANDS = {
    "up", "down", "left", "right", "select",
    "menu", "home", "home_hold", "control_center",
    "play", "pause", "play_pause",
    "next", "previous",
    "volume_up", "volume_down",
}

ACTION_MAP = {
    "tap": InputAction.SingleTap,
    "double_tap": InputAction.DoubleTap,
    "hold": InputAction.Hold,
}


class ConnectionManager:
    """Apple TV 연결을 관리한다."""

    def __init__(self):
        self._devices: dict[str, pyatv.interface.BaseConfig] = {}
        self._connections: dict[str, AppleTV] = {}
        self._pairing_handlers: dict[str, pyatv.interface.PairingHandler] = {}
        self._is_suspended = False

    def _load_credentials(self) -> dict:
        if CREDENTIALS_FILE.exists():
            return json.loads(CREDENTIALS_FILE.read_text())
        return {}

    def _save_credentials(self, data: dict):
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))

    def _apply_credentials(self, device_id: str, config: pyatv.interface.BaseConfig):
        creds = self._load_credentials().get(device_id, {})
        for protocol_name, credentials in creds.items():
            protocol = pyatv.const.Protocol[protocol_name]
            config.set_credentials(protocol, credentials)

    def has_credentials(self, device_id: str) -> bool:
        """Companion 크레덴셜이 있는지 확인한다."""
        creds = self._load_credentials().get(device_id, {})
        return "Companion" in creds

    async def scan(self, timeout: float = 5.0) -> list[dict]:
        loop = asyncio.get_event_loop()
        results = await pyatv.scan(loop, timeout=timeout)
        devices = []
        for config in results:
            device_id = str(config.identifier)
            self._devices[device_id] = config
            devices.append({
                "id": device_id,
                "name": config.name,
                "address": str(config.address),
            })
        return devices

    async def start_pairing(self, device_id: str, protocol_name: str = "Companion") -> dict:
        config = self._devices.get(device_id)
        if not config:
            raise ValueError(f"기기를 찾을 수 없습니다: {device_id}")

        protocol = pyatv.const.Protocol[protocol_name]
        handler = await pyatv.pair(config, protocol, asyncio.get_event_loop())
        await handler.begin()
        self._pairing_handlers[device_id] = handler

        return {
            "device_provides_pin": handler.device_provides_pin,
            "message": "Apple TV에 표시된 PIN을 입력하세요." if handler.device_provides_pin
            else "앱에 표시된 PIN을 Apple TV에 입력하세요.",
        }

    async def finish_pairing(self, device_id: str, pin: Optional[str] = None) -> dict:
        handler = self._pairing_handlers.get(device_id)
        if not handler:
            raise ValueError(f"진행 중인 페어링이 없습니다: {device_id}")

        if pin:
            handler.pin(int(pin))

        await handler.finish()
        paired = handler.has_paired

        if paired and handler.service.credentials:
            data = self._load_credentials()
            if device_id not in data:
                data[device_id] = {}
            data[device_id][handler.service.protocol.name] = handler.service.credentials
            self._save_credentials(data)

        await handler.close()
        del self._pairing_handlers[device_id]

        return {"paired": paired}

    async def connect(self, device_id: str) -> dict:
        if device_id in self._connections:
            self._connections[device_id].close()
            del self._connections[device_id]

        config = self._devices.get(device_id)
        if not config:
            raise ValueError(f"기기를 찾을 수 없습니다: {device_id}")

        self._apply_credentials(device_id, config)
        atv = await pyatv.connect(config, asyncio.get_event_loop())
        self._connections[device_id] = atv
        return {"status": "connected"}

    async def disconnect(self, device_id: str) -> dict:
        atv = self._connections.pop(device_id, None)
        if atv:
            atv.close()
            return {"status": "disconnected"}
        return {"status": "not_connected"}

    def get_connection(self, device_id: str) -> Optional[AppleTV]:
        return self._connections.get(device_id)

    @property
    def connected_device_id(self) -> Optional[str]:
        for device_id in self._connections:
            return device_id
        return None

    def get_connected_device_name(self) -> Optional[str]:
        device_id = self.connected_device_id
        if device_id and device_id in self._devices:
            return self._devices[device_id].name
        return None

    async def send_command(self, command: str, action: Optional[str] = None):
        """리모트 명령을 전송한다."""
        if command not in VALID_COMMANDS:
            raise ValueError(f"유효하지 않은 명령: {command}")

        device_id = self.connected_device_id
        if not device_id:
            raise RuntimeError("연결된 기기가 없습니다.")

        atv = self.get_connection(device_id)
        rc = atv.remote_control
        method = getattr(rc, command, None)
        if not method:
            raise ValueError(f"지원하지 않는 명령: {command}")

        if action and action in ACTION_MAP:
            await method(action=ACTION_MAP[action])
        else:
            await method()

    @property
    def is_suspended(self) -> bool:
        return self._is_suspended

    async def sleep(self):
        """Apple TV를 절전한다."""
        device_id = self.connected_device_id
        if not device_id:
            raise RuntimeError("연결된 기기가 없습니다.")

        atv = self.get_connection(device_id)

        from pyatv.protocols.companion.api import HidCommand
        companion_rc = atv.remote_control.get(pyatv.const.Protocol.Companion)
        if companion_rc:
            await companion_rc._press_button(HidCommand.Sleep)
        else:
            await atv.power.turn_off()
        self._is_suspended = True

    async def wake(self):
        """Apple TV를 깨운다."""
        device_id = self.connected_device_id
        if not device_id:
            raise RuntimeError("연결된 기기가 없습니다.")

        atv = self.get_connection(device_id)

        from pyatv.protocols.companion.api import HidCommand
        companion_rc = atv.remote_control.get(pyatv.const.Protocol.Companion)
        if companion_rc:
            await companion_rc._press_button(HidCommand.Wake)
        else:
            await atv.power.turn_on()
        self._is_suspended = False

    async def send_text(self, text: str):
        """Apple TV에 텍스트를 전송한다."""
        device_id = self.connected_device_id
        if not device_id:
            raise RuntimeError("연결된 기기가 없습니다.")

        atv = self.get_connection(device_id)
        await atv.keyboard.text_set(text)

    async def clear_text(self):
        """Apple TV 키보드 텍스트를 지운다."""
        device_id = self.connected_device_id
        if not device_id:
            raise RuntimeError("연결된 기기가 없습니다.")

        atv = self.get_connection(device_id)
        await atv.keyboard.text_clear()

    async def get_status(self) -> dict:
        """현재 재생 상태를 반환한다."""
        device_id = self.connected_device_id
        if not device_id:
            return {"connected": False}

        atv = self.get_connection(device_id)
        try:
            playing = await atv.metadata.playing()
            app_info = atv.metadata.app
            return {
                "connected": True,
                "app": app_info.name if app_info else None,
                "title": playing.title,
                "artist": playing.artist,
            }
        except Exception as e:
            return {"connected": True, "error": str(e)}

    async def shutdown(self):
        for handler in self._pairing_handlers.values():
            await handler.close()
        self._pairing_handlers.clear()

        for atv in self._connections.values():
            atv.close()
        self._connections.clear()
