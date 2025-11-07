import asyncio
from playwright.async_api import Page
from ig_cleaner.utils import random_delay

async def delete_posts(page: Page, username: str, count: int):
    """
    Navigates to the user's profile, collects post links, and deletes them.
    """
    print(f"Открытие профиля: https://www.instagram.com/{username}/")
    await page.goto(f"https://www.instagram.com/{username}/", wait_until='domcontentloaded')

    # Проверка, залогинен ли пользователь
    await asyncio.sleep(5) # Даем странице время на редирект, если не залогинен
    if "login" in page.url:
        print("Ошибка: Пользователь не залогинен в Instagram в этом профиле MoreLogin.")
        print("Пожалуйста, войдите в аккаунт Instagram и перезапустите скрипт.")
        return

    print("Собираем посты для удаления...")
    post_links = set()
    post_selector = 'a[href*="/p/"], a[href*="/reel/"]'

    try:
        await page.wait_for_selector(post_selector, timeout=20000)
    except Exception:
        print("Не удалось найти посты на странице. Возможно, профиль пуст или Instagram изменил верстку.")
        return

    links = await page.query_selector_all(post_selector)
    for link in links:
        href = await link.get_attribute('href')
        if href:
            post_links.add(f"https://www.instagram.com{href}")

    if not post_links:
        print("Не найдено постов для удаления.")
        return

    posts_to_delete = list(post_links)[:count]
    print(f"Найдено {len(posts_to_delete)} постов для удаления.")

    deleted_count = 0
    for i, post_url in enumerate(posts_to_delete):
        print(f"Удаление поста {i + 1}/{len(posts_to_delete)}")
        try:
            await page.goto(post_url)
            await random_delay()

            options_button_selector = 'svg[aria-label="More options"]'
            await page.wait_for_selector(options_button_selector, timeout=15000)
            await page.locator(options_button_selector).first.click()
            await random_delay()

            await page.get_by_text("Delete").first.click()
            await random_delay()

            # Подтверждение удаления во всплывающем окне
            delete_button_in_dialog = 'button:has-text("Delete")'
            await page.wait_for_selector(delete_button_in_dialog)
            await page.locator(delete_button_in_dialog).first.click()

            print(f"Пост {i + 1} успешно удален.")
            deleted_count += 1
            await random_delay(3, 5)

        except Exception as e:
            print(f"Не удалось удалить пост {i + 1}. Ошибка: {e}")
            print("Пропускаем и переходим к следующему.")
            continue

    return deleted_count
