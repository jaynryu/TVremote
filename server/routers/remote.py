from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from pyatv.const import InputAction

from connection_manager import manager

router = APIRouter(prefix="/remote", tags=["remote"])

VALID_COMMANDS = {
    "up", "down", "left", "right", "select",
    "menu", "home", "home_hold",
    "play", "pause", "play_pause",
    "next", "previous",
    "volume_up", "volume_down",
}

ACTION_MAP = {
    "tap": InputAction.SingleTap,
    "double_tap": InputAction.DoubleTap,
    "hold": InputAction.Hold,
}


class RemoteCommand(BaseModel):
    action: Optional[str] = None  # tap, double_tap, hold


@router.post("/{command}")
async def send_command(command: str, body: RemoteCommand = RemoteCommand()):
    """리모트 명령을 전송한다."""
    if command not in VALID_COMMANDS:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 명령: {command}. 가능한 명령: {', '.join(sorted(VALID_COMMANDS))}",
        )

    device_id = manager.connected_device_id
    if not device_id:
        raise HTTPException(status_code=400, detail="연결된 기기가 없습니다.")

    atv = manager.get_connection(device_id)
    rc = atv.remote_control
    method = getattr(rc, command, None)

    if not method:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 명령: {command}")

    try:
        if body.action and body.action in ACTION_MAP:
            await method(action=ACTION_MAP[body.action])
        else:
            await method()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "command": command}


@router.post("/power/toggle")
async def power_toggle():
    """전원을 켜거나 끈다."""
    device_id = manager.connected_device_id
    if not device_id:
        raise HTTPException(status_code=400, detail="연결된 기기가 없습니다.")

    atv = manager.get_connection(device_id)
    try:
        from pyatv.const import PowerState
        if atv.power.power_state == PowerState.On:
            await atv.power.turn_off()
        else:
            await atv.power.turn_on()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
