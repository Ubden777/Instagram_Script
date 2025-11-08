import time
import random
import os
from playwright.sync_api import Page, TimeoutError

def _random_sleep(a=1.5, b=3.0):
    """Случайная пауза для имитации человеческого поведения."""
    time.sleep(random.uniform(a, b))

def _retry_click(page: Page, selectors: list, max_attempts=3, timeout=2500):
    """
    Пытается кликнуть по элементу, перебирая список селекторов.
    Возвращает (True, attempts) при успехе, (False, attempts) при неудаче.
    """
    for attempt in range(1, max_attempts + 1):
        for selector in selectors:
            try:
                page.click(selector, timeout=timeout)
                return True, attempt
            except TimeoutError:
                continue # Попробовать следующий селектор
            except Exception:
                continue # Другие ошибки тоже пропускаем
        _random_sleep(0.5, 1.0) # Пауза перед следующей общей попыткой
    return False, max_attempts

def collect_posts(page: Page, logger, username: str, limit=25):
    """
    Собирает URL постов, прокручивая страницу.
    Возвращает список URL.
    """
    print("Открытие профиля и сбор постов...")
    page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded")
    _random_sleep(3, 5)

    # Проверка на страницу логина
    if "login" in page.url.lower():
        print("ОШИБКА: Профиль не авторизован. Пожалуйста, войдите в Instagram.")
        logger.log(post_url='n/a', status='error', error_message='Not logged in')
        return None

    urls = set()
    last_height = 0
    while len(urls) < limit:
        new_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
        for link in new_links:
            href = link.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else f"https://www.instagram.com{href}"
                urls.add(full_url)

        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == last_height:
            print(f"Скроллинг завершен. Собрано {len(urls)} уникальных постов.")
            break

        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        last_height = current_height
        _random_sleep(2, 4)

    return list(urls)[:limit]

def delete_posts(page: Page, logger, username: str, count=25, dry_run=False):
    """
    Удаляет посты, используя fail-retry логику и детальное логирование.
    """
    urls = collect_posts(page, logger, username, count)
    if urls is None: # Ошибка авторизации
        return 0

    if not urls:
        print("Посты для удаления не найдены.")
        logger.log(post_url='n/a', status='not_found', error_message='No posts found on the page')
        return 0

    if dry_run:
        print(f"\n[DRY-RUN] Найдено {len(urls)} постов. Они будут записаны в CSV, но не удалены.")
        for url in urls:
            logger.log(post_url=url, status='skipped', dry_run=True)
        return 0

    print(f"Начинается удаление {len(urls)} постов...")
    deleted_count = 0

    menu_selectors = ['svg[aria-label*="options" i]','button[aria-label*="options" i]','svg[aria-label*="варианты" i]']
    delete_texts = ["Delete", "Удалить", "Eliminar", "Supprimer"]
    confirm_texts = ["Delete", "Удалить", "Confirm"]

    for url in urls:
        screenshot_path = ''
        try:
            page.goto(url, wait_until="domcontentloaded")
            _random_sleep(2, 3)

            # 1. Клик по меню "More options"
            menu_clicked, menu_attempts = _retry_click(page, menu_selectors)
            if not menu_clicked:
                raise RuntimeError("Не удалось найти и кликнуть кнопку меню.")

            # 2. Клик по кнопке "Delete"
            delete_selectors = [f'text="{txt}"' for txt in delete_texts]
            delete_clicked, delete_attempts = _retry_click(page, delete_selectors)
            if not delete_clicked:
                raise RuntimeError("Не удалось найти и кликнуть кнопку 'Удалить'.")

            # 3. Клик по кнопке подтверждения
            confirm_selectors = [f'button:has-text("{txt}")' for txt in confirm_texts]
            confirm_clicked, confirm_attempts = _retry_click(page, confirm_selectors, max_attempts=2)
            if not confirm_clicked:
                # Иногда подтверждение не требуется, не считаем это фатальной ошибкой
                print("Кнопка подтверждения не найдена, возможно, она не требуется.")

            deleted_count += 1
            print(f"УСПЕХ: Пост {url} удален.")
            logger.log(post_url=url, status='deleted', attempts=menu_attempts + delete_attempts + confirm_attempts, delete_action='success')

        except Exception as e:
            error_message = str(e).split('\n')[0]
            print(f"ОШИБКА: Не удалось удалить пост {url}. Причина: {error_message}")

            try:
                path = os.path.join("logs", f"error_{username}_{int(time.time())}.png")
                page.screenshot(path=path)
                screenshot_path = path
            except Exception as se:
                print(f"Не удалось сделать скриншот: {se}")

            logger.log(post_url=url, status='error', error_message=error_message, screenshot_path=screenshot_path)
            continue

    return deleted_count
