import asyncio
from pathlib import Path
from typing import List

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page


class User:
    def __init__(self, element: ElementHandle):
        self.element = element

    async def get_id(self) -> str:
        prop: ElementHandle = await self.element.getProperty("id")
        uid: str = prop.toString()[5:]
        return uid

    async def get_frame(self) -> bytes:
        frame: bytes = await self.element.screenshot()
        return frame

    @property
    def id(self):
        return asyncio.run(self.get_id())

    @property
    def frame(self):
        return asyncio.run(self.get_frame())


class AgoraRTC:
    def __init__(self, app_id: str, channel_name: str):
        self.app_id = app_id
        self.channel_name = channel_name
        self.browser = None

    async def __aenter__(self):
        self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], headless=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self.browser is not None
        await self.browser.close()

    async def open(self):
        self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], headless=False)

    async def close(self):
        assert self.browser is not None
        await self.browser.close()

    # def open(self):
    #     asyncio.run(self.async_open())
    #
    # def close(self):
    #     asyncio.run(self.async_close())
    #
    # def __enter__(self):
    #     self.open()
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.close()

    async def get_users_list(self) -> List[ElementHandle]:
        assert self.browser is not None

        page: Page = await self.browser.newPage()
        frontend_html: Path = Path("./frontend/index.html").absolute()
        await page.goto(f"file://{str(frontend_html)}")
        await page.waitForFunction("bootstrap", None, self.app_id, self.channel_name)
        await page.waitForSelector("video")
        users: List[ElementHandle] = await page.JJ("video")

        return users

    async def get_users(self) -> List[User]:
        assert self.browser is not None

        # print("test1")
        # self.loop = asyncio.get_running_loop()
        # asyncio.set_event_loop(loop)
        # print("test2")
        # print(asyncio.get_running_loop())
        results: List[ElementHandle] = await self.get_users_list()
        return [User(result) for result in results]
