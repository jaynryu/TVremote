import asyncio
import json
from pathlib import Path
from typing import Optional

import pyatv
from pyatv.interface import AppleTV

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"


class ConnectionManager:
    """Apple TV 연결을 관리하는 싱글톤 클래스."""

    def __init__(self):
        self._devices: dict[str, pyatv.interface.BaseConfig] = {}
        self._connections: dict[str, AppleTV] = {}
        self._pairing_handlers: dict[str, pyatv.interface.PairingHandler] = {}

    def _load_credentials(self) -> dict:
        if CREDENTIALS_FILE.exists():
            return json.loads(CREDENTIALS_FILE.read_text())
        return {}

    def _apply_credentials(self, device_id: str, config: pyatv.interface.BaseConfig):
        """저장된 credential을 config에 적용한다."""
        creds = self._load_credentials().get(device_id, {})
        for protocol_name, credentials in creds.items():
            protocol = pyatv.const.Protocol[protocol_name]
            config.set_credentials(protocol, credentials)

    async def scan(self, timeout: float = 5.0) -> list[dict]:
        """로컬 네트워크에서 Apple TV 기기를 검색한다."""
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
        """페어링을 시작한다. Apple TV에 PIN이 표시된다."""
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
        """PIN을 입력하고 페어링을 완료한다."""
        handler = self._pairing_handlers.get(device_id)
        if not handler:
            raise ValueError(f"진행 중인 페어링이 없습니다: {device_id}")

        if pin:
            handler.pin(int(pin))

        await handler.finish()
        paired = handler.has_paired

        if paired and handler.service.credentials:
            data = self._load_credentials()
            device_id_key = device_id
            if device_id_key not in data:
                data[device_id_key] = {}
            data[device_id_key][handler.service.protocol.name] = handler.service.credentials
            CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))

        await handler.close()
        del self._pairing_handlers[device_id]

        return {"paired": paired}

    async def connect(self, device_id: str) -> dict:
        """Apple TV에 연결한다. 기존 연결이 있으면 끊고 재연결한다."""
        # 기존 연결이 있으면 먼저 정리
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
        """Apple TV 연결을 해제한다."""
        atv = self._connections.pop(device_id, None)
        if atv:
            atv.close()
            return {"status": "disconnected"}
        return {"status": "not_connected"}

    def get_connection(self, device_id: str) -> Optional[AppleTV]:
        """연결된 Apple TV 인스턴스를 반환한다."""
        return self._connections.get(device_id)

    @property
    def connected_device_id(self) -> Optional[str]:
        """현재 연결된 첫 번째 기기 ID를 반환한다."""
        for device_id in self._connections:
            return device_id
        return None

    async def shutdown(self):
        """모든 연결을 정리한다."""
        for handler in self._pairing_handlers.values():
            await handler.close()
        self._pairing_handlers.clear()

        for atv in self._connections.values():
            atv.close()
        self._connections.clear()


manager = ConnectionManager()
