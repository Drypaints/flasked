import asyncio
from dotenv import load_dotenv
import os
from playwright.async_api import async_playwright, Page

load_dotenv()


class Bot:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.username = "admin"
        self.password = os.getenv("ADMIN_APP_PASSWORD")
        if not self.password:
            raise ValueError("ADMIN_APP_PASSWORD is not set in the .env file")

    async def login(self, page: Page):
        await page.goto(f"{self.base_url}/login")
        await page.fill('input[name="username"]', self.username)
        await page.fill('input[name="password"]', self.password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("domcontentloaded")

    async def visit(self, link: str):
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await self.login(page)
                await page.wait_for_load_state(timeout=2000)
                await page.goto(link)
                await page.wait_for_load_state("domcontentloaded", timeout=2000)
                await page.wait_for_timeout(5000)
                print(f"[+] Bot is visiting: {link}")
            finally:
                await browser.close()
                print("[+] Bot session closed.")


# Entry point for quick manual test
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python bot.py <url>")
    else:
        asyncio.run(Bot().visit(sys.argv[1]))
