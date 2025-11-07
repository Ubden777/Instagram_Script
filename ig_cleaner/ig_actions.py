import os
from playwright.sync_api import Page
from ig_cleaner.utils import random_delay

def delete_posts(page: Page, username: str, count: int = 25):
    print("🔍 Открываю профиль Instagram…")
    page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
    page.wait_for_load_state("networkidle")
    random_delay(2, 5)

    posts = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    print(f"Найдено {len(posts)} постов, удаляем {count}")
    posts = posts[:count]

    os.makedirs("logs", exist_ok=True)
    for i, post in enumerate(posts, start=1):
        try:
            href = post.get_attribute("href")
            print(f"🗑️ Удаляю {href}")
            page.goto(f"https://www.instagram.com{href}", timeout=60000)
            random_delay(2, 5)

            page.get_by_role("button", name="More options").click()
            random_delay(1, 3)
            delete_btn = page.get_by_role("button", name="Delete")
            if not delete_btn.is_visible():
                delete_btn = page.get_by_text("Удалить")
            delete_btn.click()
            random_delay(1, 2)
            page.get_by_role("button", name="Delete").click()
            random_delay(3, 6)
        except Exception as e:
            path = f"logs/error_{username}_{i}.png"
            page.screenshot(path=path)
            print(f"⚠️ Ошибка при удалении поста {i}: {e} (сохранён скриншот {path})")

    print("✅ Удаление завершено")
