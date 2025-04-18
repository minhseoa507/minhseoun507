# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import random
import string
import os

# Cấu hình
URL_REGISTER = "https://gpoesteso.com/index/user/register"
INVITE_CODE = "268268"
NUM_WORKERS = 3
PASSWORD = "456789"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

if not os.path.exists("errorshots"):
    os.makedirs("errorshots")

def fake_vn_phone():
    prefix_list = ["032", "033", "034", "035", "036", "037", "038", "039",
                   "070", "076", "077", "078", "079",
                   "081", "082", "083", "084", "085", "086", "088", "089",
                   "090", "091", "092", "093", "094", "095", "096", "097", "098", "099"]
    prefix = random.choice(prefix_list)
    number = ''.join(random.choices("0123456789", k=7))
    return prefix + number

def fake_user():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    phone = fake_vn_phone()
    return username, phone, PASSWORD

async def register_forever(index, browser):
    while True:
        username, phone, password = fake_user()
        try:
            context = await browser.new_context(user_agent=UA, locale="en-US")
            page = await context.new_page()

            print(f"[luồng {index}] Đăng ký: {username} | {phone}")
            await page.goto(URL_REGISTER, timeout=60000)

            # Điền form đăng ký
            await page.fill('input[placeholder="Your username"]', username)
            await page.fill('input[placeholder="Your phone numbers"]', phone)
            await page.fill('input[placeholder="Login password"]', password)

            if await page.query_selector('input[placeholder="Confirm Password"]'):
                await page.fill('input[placeholder="Confirm Password"]', password)

            if await page.query_selector('input[placeholder="Enter fund password"]'):
                await page.fill('input[placeholder="Enter fund password"]', password)

            await page.wait_for_selector('input[name="invite_code"]', timeout=10000)
            await page.fill('input[name="invite_code"]', INVITE_CODE)

            # Click nút đăng ký
            await page.wait_for_selector('a.form-buttom')
            await page.click('a.form-buttom')

            # Chờ xử lý + kiểm tra redirect
            await page.wait_for_timeout(3000)
            current_url = page.url

            if "/login" in current_url:
                print(f"[luồng {index}] ✅ Đăng ký thành công: {username}")
            else:
                print(f"[luồng {index}] ❌ Đăng ký thất bại: {username}")
                await page.screenshot(path=f"errorshots/luong{index}_{username}_fail.png")

            await page.close()
            await context.close()

        except Exception as e:
            print(f"[luồng {index}] ❌ Lỗi: {e}")
            try:
                await page.screenshot(path=f"errorshots/luong{index}_{username}_error.png")
            except:
                pass

        await asyncio.sleep(random.uniform(2, 4))

async def main():
    try:
        print("🚀 Khởi chạy Playwright...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=["--window-position=-32000,-32000"]
            )
            tasks = [register_forever(i + 1, browser) for i in range(NUM_WORKERS)]
            await asyncio.gather(*tasks)
    except Exception as err:
        print(f"❗ Lỗi xảy ra trong khi chạy main(): {err}")
        input("Ấn Enter để thoát...")

if __name__ == "__main__":
    asyncio.run(main())
