# ig_actions.py (фрагмент: заменить функцию delete_posts)
import asyncio
import os
import random
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from ig_cleaner.utils import random_delay

async def delete_posts(page: Page, username: str, count: int):
    """
    Opens profile, collects latest posts (including /p/ and /reel/) and deletes them one by one.
    Returns number of actually deleted posts.
    """
    print(f"Открытие профиля: https://www.instagram.com/{username}/")
    await page.goto(f"https://www.instagram.com/{username}/", wait_until='domcontentloaded')
    await asyncio.sleep(4)  # дать время на возможный редирект

    # проверим залогинен ли профиль
    current_url = page.url
    if "login" in current_url:
        print("Ошибка: профиль не авторизован в Instagram (MoreLogin).")
        return 0

    # Собираем ссылки: /p/ и /reel/
    print("Собираем посты для удаления...")
    await asyncio.sleep(2)
    links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    post_urls = []
    for l in links:
        href = await l.get_attribute('href')
        if not href:
            continue
        full = href if href.startswith("http") else f"https://www.instagram.com{href}"
        if full not in post_urls:
            post_urls.append(full)
        if len(post_urls) >= count:
            break

    if not post_urls:
        print("Не найдено постов для удаления.")
        return 0

    print(f"Найдено постов: {len(post_urls)}. Начинаю удаление...")
    deleted_count = 0

    for i, post_url in enumerate(post_urls):
        print(f"[{i+1}/{len(post_urls)}] Открываю {post_url}")
        try:
            await page.goto(post_url, wait_until='domcontentloaded')
            # Небольшая пауза
            await asyncio.sleep(1.5)

            # Попытаемся найти кнопку "More options" (три точки) через aria-label (на разных языках)
            options_selectors = [
                'svg[aria-label="More options"]',      # английский svg aria
                'button[aria-label="More options"]',
                'svg[aria-label="Еще варианты"]',      # пример на русском (может отличаться)
                'button[aria-label="Еще варианты"]',
                'svg[aria-label="Опции"]',
                'button[aria-label="Опции"]'
            ]
            clicked = False
            for sel in options_selectors:
                try:
                    await page.wait_for_selector(sel, timeout=3000)
                    await page.click(sel)
                    clicked = True
                    break
                except PlaywrightTimeoutError:
                    continue

            if not clicked:
                # fallback: искать кнопку по role/aria-haspopup или по наличию трёх точек в DOM
                try:
                    await page.click('button[aria-haspopup="menu"]', timeout=3000)
                    clicked = True
                except PlaywrightTimeoutError:
                    pass

            # Кликнули на меню — теперь ищем Delete по тексту (англ) и возможным локалям
            delete_texts = ["Delete", "Удалить", "Eliminar", "Supprimer"]
            deleted_clicked = False
            for txt in delete_texts:
                try:
                    await page.click(f'text="{txt}"', timeout=2500)
                    deleted_clicked = True
                    break
                except PlaywrightTimeoutError:
                    continue

            if not deleted_clicked:
                # Возможно меню открылось как диалог — попробуем искать кнопку подтверждения удаления
                print("Кнопка 'Delete' не найдена, пропускаю пост.")
                continue

            # Подтверждение удаления (в диалоге)
            try:
                await page.wait_for_selector('button:has-text("Delete")', timeout=4000)
                await page.click('button:has-text("Delete")')
            except PlaywrightTimeoutError:
                # попробуем русскоязычный
                try:
                    await page.wait_for_selector('button:has-text("Удалить")', timeout=2000)
                    await page.click('button:has-text("Удалить")')
                except PlaywrightTimeoutError:
                    print("Не удалось подтвердить удаление (кнопка подтверждения не найдена). Пропуск.")
                    continue

            # Ждём небольшой интервал после удаления
            await asyncio.sleep(1.5)
            deleted_count += 1
            print(f"Пост {i+1} успешно удалён.")
            await random_delay(2, 4)

        except Exception as e:
            # Сохраним скриншот для дебага
            try:
                logs_dir = "logs"
                os.makedirs(logs_dir, exist_ok=True)
                path = os.path.join(logs_dir, f"error_delete_{username}_{i+1}.png")
                await page.screenshot(path=path)
                print(f"Скриншот сохранён: {path}")
            except Exception as screenshot_error:
                print(f"Не удалось сохранить скриншот: {screenshot_error}")
            print(f"Ошибка при удалении поста {post_url}: {e}")
            continue

    return deleted_count
