from typing import List, Tuple

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page


async def get_users_list(app_id: str, channel_name: str) -> List[ElementHandle]:
    browser: Browser = await launch()
    page: Page = await browser.newPage()
    await page.goto("localhost:3097")
    await page.waitForFunction("bootstrap", None, app_id, channel_name)
    await page.waitForSelector("video")
    users: List[ElementHandle] = await page.JJ("video")

    return users


async def get_user(user: ElementHandle) -> Tuple[str, bytes]:
    prop: ElementHandle = await user.getProperty("id")
    uid: str = prop.toString()
    frame: bytes = await user.screenshot()
    return uid, frame
