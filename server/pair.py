import asyncio
import json
import sys
from pathlib import Path

import pyatv

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"


def load_credentials():
    if CREDENTIALS_FILE.exists():
        return json.loads(CREDENTIALS_FILE.read_text())
    return {}


def save_credentials(device_id, protocol_name, credentials):
    data = load_credentials()
    if device_id not in data:
        data[device_id] = {}
    data[device_id][protocol_name] = credentials
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))


async def main():
    loop = asyncio.get_event_loop()
    protocol_name = sys.argv[1] if len(sys.argv) > 1 else "Companion"
    protocol = pyatv.const.Protocol[protocol_name]

    print("기기 검색 중...")
    devices = await pyatv.scan(loop, timeout=5)
    atv = None
    for d in devices:
        if "안방" in d.name:
            atv = d
            break

    if not atv:
        print("Apple TV를 찾지 못했습니다.")
        return

    device_id = str(atv.identifier)
    print(f"기기: {atv.name} ({atv.address})")
    print(f"프로토콜: {protocol_name}")
    print()

    pairing = await pyatv.pair(atv, protocol, loop)
    await pairing.begin()

    if pairing.device_provides_pin:
        print("Apple TV 화면에 표시된 PIN을 입력하세요:")
    else:
        print("앱에 표시된 PIN을 Apple TV에 입력하세요.")

    pin = await loop.run_in_executor(None, lambda: input("PIN: "))
    pairing.pin(int(pin))
    await pairing.finish()

    if pairing.has_paired:
        creds = pairing.service.credentials
        save_credentials(device_id, protocol_name, creds)
        print(f"\n페어링 성공! credential 저장됨 → {CREDENTIALS_FILE}")
    else:
        print("\n페어링 실패")

    await pairing.close()


asyncio.run(main())
