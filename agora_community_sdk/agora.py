import asyncio
import os
from asyncio.events import AbstractEventLoop
from pathlib import Path
from typing import List, Optional, Union

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page
import threading


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
        frame: bytes = await self.element.screenshot()
        return frame

    @property
    def id(self):
        return self.loop.run_until_complete(self.get_id())

    @property
    def frame(self):
        return self.loop.run_until_complete(self.get_frame())


class AgoraRTC:
    page: Optional[Page]
    loop: AbstractEventLoop
    channel_name: Optional[str]
    app_id: str
    browser: Optional[Browser]

    def __init__(self, app_id: str, loop):
        self.app_id = app_id
        self.channel_name = None
        self.loop = loop
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    @classmethod
    def create_watcher(cls, app_id: str):
        loop = asyncio.get_event_loop()
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
        self.loop.run_until_complete(self.creator())

    async def async_close(self):
        assert self.browser is not None
        await self.browser.close()

    def unwatch(self):
        self.loop.run_until_complete(self.async_close())

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
        return self.loop.run_until_complete(self.async_get_users())
