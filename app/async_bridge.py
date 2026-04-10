"""백그라운드 asyncio 이벤트 루프를 관리하는 브릿지."""

import asyncio
import threading
from typing import Any, Callable, Coroutine, Optional


class AsyncBridge:
    """tkinter 메인 스레드와 asyncio 백그라운드 스레드를 연결한다."""

    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """백그라운드 asyncio 이벤트 루프를 시작한다."""
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Coroutine) -> asyncio.Future:
        """코루틴을 백그라운드 루프에 제출하고 Future를 반환한다."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_with_callback(
        self,
        coro: Coroutine,
        root,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """코루틴을 실행하고 결과를 tkinter 메인 스레드에서 콜백한다."""
        future = self.run(coro)

        def _check():
            if not future.done():
                root.after(50, _check)
                return
            try:
                result = future.result()
                if on_success:
                    on_success(result)
            except Exception as e:
                if on_error:
                    on_error(e)

        root.after(50, _check)

    def shutdown(self):
        """이벤트 루프를 종료한다."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=3)
