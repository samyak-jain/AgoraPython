import asyncio
import os
import threading
import time
from asyncio.events import AbstractEventLoop
from pathlib import Path
from threading import Lock
from typing import List, Optional, Union, Callable, Any, Tuple, Dict

import nest_asyncio
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page


def run_async_code(function: Callable[..., Any], loop: AbstractEventLoop) -> Any:
    # task = loop.create_task(function())

    # future = asyncio.run_coroutine_threadsafe(function(), loop)
    # # return future.done()
    # try:
    #     result = future.result()
    # except asyncio.TimeoutError:
    #     print("Coroutine took long. Cancelling...")
    #     future.cancel()
    # else:
    #     return result
    return loop.run_until_complete(function())


class User:
    loop: AbstractEventLoop
    element: ElementHandle

    def __init__(self, element: ElementHandle, loop: AbstractEventLoop):
        self.element = element
        self.loop = loop

    async def get_id(self) -> str:
        prop: ElementHandle = await self.element.getProperty("id")
        uid: str = prop.toString()[14:]
        return uid

    async def get_frame(self) -> bytes:
        print(self.element)
        frame: bytes = await self.element.screenshot()
        return frame

    @property
    def id(self):
        return run_async_code(self.get_id, self.loop)

    @property
    def frame(self):
        return run_async_code(self.get_frame, self.loop)


class Locker:
    value: Any
    lock: Lock

    def __init__(self, value: Any):
        self.lock = threading.Lock()
        self.value = value


class FrameThread(threading.Thread):
    delay: float
    proc: Callable[..., Any]
    index: int

    def __init__(self, index: int, process: Callable[..., Any], delay: float):
        super().__init__()
        self.index = index
        self.proc = process  # type: ignore
        self.delay = delay

    def run(self) -> None:
        time.sleep(self.index * self.delay)
        self.proc()


class AgoraRTC:
    locked_variables: Dict[str, Locker]
    fps: Optional[int]
    page: Optional[Page]
    browser: Optional[Browser]
    loop: AbstractEventLoop
    channel_name: Optional[str]
    app_id: str

    def __init__(self, app_id: str, loop: AbstractEventLoop):
        self.app_id = app_id
        self.channel_name = None
        self.loop = loop
        self.browser = None
        self.page = None
        self.fps = None
        self.locked_variables = dict()

    @classmethod
    def create_watcher(cls, app_id: str):
        loop = asyncio.get_event_loop()
        nest_asyncio.apply(loop)
        return AgoraRTC(app_id, loop)

    async def creator(self):
        self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        self.page = await self.browser.newPage()
        current_os_path: Union[bytes, str] = os.path.dirname(os.path.realpath(__file__))
        if isinstance(current_os_path, bytes):
            current_path: str = current_os_path.decode("utf-8")
        else:
            current_path = current_os_path

        frontend_html: Path = Path(current_path) / Path("frontend/index.html")
        await self.page.goto(f"file://{str(frontend_html)}")
        await self.page.waitForFunction("bootstrap", None, self.app_id, self.channel_name)
        await self.page.waitForSelector("video.playing")

    def join_channel(self, channel_name: str):
        self.channel_name = channel_name
        # self.loop.run_until_complete(self.creator())
        run_async_code(self.creator, self.loop)

    async def async_close(self):
        assert self.browser is not None
        await self.browser.close()

    def unwatch(self):
        run_async_code(self.async_close, self.loop)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unwatch()

    async def get_users_list(self) -> List[ElementHandle]:
        assert self.browser is not None
        assert self.page is not None

        users: List[ElementHandle] = await self.page.JJ("video.playing")

        return users

    async def async_get_users(self) -> List[User]:
        assert self.browser is not None

        results: List[ElementHandle] = await self.get_users_list()
        return [User(result, self.loop) for result in results]

    def get_users(self) -> List[User]:
        return run_async_code(self.async_get_users, self.loop)

    def set_fps(self, fps: int = 30):
        if fps <= 0:
            raise ValueError("FPS value should be more than 0")

        self.fps = fps

    def get_frames(self, proc: Callable[..., Any], locker: Tuple[Any, ...] = ()):
        if self.fps is None:
            raise RuntimeError("FPS not set by the user. Use set_fps() method")

        self.locked_variables = {variable: Locker(value) for variable, value in locals().items() if value in locker}
        milliseconds_to_wait: float = 100 / self.fps

        print(self.fps)
        print(milliseconds_to_wait)

        threads = [FrameThread(index, proc, milliseconds_to_wait) for index in range(self.fps)]
        for thread in threads:
            thread.start()
