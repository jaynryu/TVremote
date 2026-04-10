from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from connection_manager import manager
from routers import devices, remote, keyboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await manager.shutdown()


app = FastAPI(
    title="Apple TV Remote API",
    description="Apple TV를 제어하는 REST API 서버",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router)
app.include_router(remote.router)
app.include_router(keyboard.router)


@app.get("/status")
async def get_status():
    """현재 재생 상태를 반환한다."""
    device_id = manager.connected_device_id
    if not device_id:
        return {"connected": False}

    atv = manager.get_connection(device_id)
    try:
        playing = await atv.metadata.playing()
        app_info = atv.metadata.app
        return {
            "connected": True,
            "device_id": device_id,
            "app": app_info.name if app_info else None,
            "title": playing.title,
            "artist": playing.artist,
            "media_type": str(playing.media_type),
            "device_state": str(playing.device_state),
            "position": playing.position,
            "total_time": playing.total_time,
        }
    except Exception as e:
        return {"connected": True, "device_id": device_id, "error": str(e)}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
