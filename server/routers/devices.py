from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from connection_manager import manager

router = APIRouter(prefix="/devices", tags=["devices"])


class PinRequest(BaseModel):
    pin: str


class PairRequest(BaseModel):
    protocol: str = "companion"


@router.get("")
async def scan_devices(timeout: float = 5.0):
    """로컬 네트워크에서 Apple TV 기기를 검색한다."""
    devices = await manager.scan(timeout=timeout)
    return {"devices": devices}


@router.post("/{device_id}/pair")
async def start_pairing(device_id: str, request: PairRequest = PairRequest()):
    """페어링을 시작한다."""
    try:
        result = await manager.start_pairing(device_id, request.protocol)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/pair/pin")
async def finish_pairing(device_id: str, request: PinRequest):
    """PIN을 입력하고 페어링을 완료한다."""
    try:
        result = await manager.finish_pairing(device_id, request.pin)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/connect")
async def connect_device(device_id: str):
    """Apple TV에 연결한다."""
    try:
        result = await manager.connect(device_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/disconnect")
async def disconnect_device(device_id: str):
    """Apple TV 연결을 해제한다."""
    result = await manager.disconnect(device_id)
    return result
