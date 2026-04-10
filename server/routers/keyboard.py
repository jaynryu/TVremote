from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from connection_manager import manager

router = APIRouter(prefix="/keyboard", tags=["keyboard"])


class TextInput(BaseModel):
    text: str


@router.post("")
async def send_text(body: TextInput):
    """Apple TV에 텍스트를 전송한다."""
    device_id = manager.connected_device_id
    if not device_id:
        raise HTTPException(status_code=400, detail="연결된 기기가 없습니다.")

    atv = manager.get_connection(device_id)

    try:
        keyboard = atv.keyboard
        await keyboard.text_set(body.text)
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="키보드 입력을 사용하려면 Companion 프로토콜로 페어링이 필요합니다.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "text": body.text}


@router.post("/clear")
async def clear_text():
    """Apple TV 키보드 텍스트를 지운다."""
    device_id = manager.connected_device_id
    if not device_id:
        raise HTTPException(status_code=400, detail="연결된 기기가 없습니다.")

    atv = manager.get_connection(device_id)

    try:
        keyboard = atv.keyboard
        await keyboard.text_clear()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
