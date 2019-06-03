import asyncio
from pathlib import Path
from typing import List

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page


class User:
    def __init__(self, element: ElementHandle):
        self.element = element

    def get_id(self) -> str:
        prop: ElementHandle = await self.element.getProperty("id")
        uid: str = prop.toString()[5:]
        return uid

    def get_frame(self) -> bytes:
        frame: bytes = await self.element.screenshot()
        return frame


class AgoraRTC:
    def __init__(self, app_id: str, channel_name: str):
        self.app_id = app_id
        self.channel_name = channel_name
        self.browser = None

    def open(self):
        self.browser = await launch()

    def close(self):
        assert self.browser is not None
        await self.browser.close()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def get_users_list(self, app_id: str, channel_name: str) -> List[ElementHandle]:
        page: Page = await self.browser.newPage()
        frontend_html: Path = Path("./frontend/index.html").absolute()
        await page.goto(f"file://{str(frontend_html)}")
        await page.waitForFunction("bootstrap", None, app_id, channel_name)
        await page.waitForSelector("video")
        users: List[ElementHandle] = await page.JJ("video")

        return users

    def get_users(self) -> List[User]:
        assert self.browser is not None

        results: List[ElementHandle] = asyncio.run(self.get_users_list(self.app_id, self.channel_name))
        return [User(result) for result in results]
