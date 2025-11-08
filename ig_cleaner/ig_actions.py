# ig_actions.py (sync delete_posts)
import os, time, random
from playwright.sync_api import TimeoutError

def random_delay(a=1.5, b=3.0):
    time.sleep(random.uniform(a, b))

def delete_posts(page, username, count=25):
    """
    Удаляет до `count` последних постов (включая reels) из профиля username,
    возвращает количество удалённых постов.
    """
    os.makedirs("logs", exist_ok=True)
    page.goto(f"https://www.instagram.com/{username}/", wait_until="load")
    random_delay(2,4)
    if "login" in page.url or "accounts/login" in page.url:
        print("Похоже, профиль не залогинен в MoreLogin.")
        return 0

    # Собрать ссылки на посты (anchors с /p/ или /reel/)
    links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    urls = []
    for a in links:
        href = a.get_attribute("href")
        if href:
            full = href if href.startswith("http") else f"https://www.instagram.com{href}"
            if full not in urls:
                urls.append(full)
        if len(urls) >= count:
            break
    if not urls:
        print("Посты не найдены.")
        return 0

    deleted = 0
    # варианты селекторов для "меню" (разные локали/DOM)
    options = [
        'svg[aria-label="More options"]',
        'button[aria-label="More options"]',
        'svg[aria-label="Опции"]',
        'button[aria-label="Опции"]',
        'svg[aria-label="Еще варианты"]',
        'button[aria-label="Еще варианты"]',
        'button[aria-label="More"]',
        'button[aria-label="Options"]',
        'div[role="button"][aria-haspopup="menu"]'
    ]
    # варианты текста для "Delete"
    delete_texts = ["Delete","Удалить","Eliminar","Supprimer","Eliminar publicación","Löschen","Deletar"]

    for i, url in enumerate(urls, start=1):
        try:
            page.goto(url, wait_until="load")
            random_delay(1.0, 2.5)

            # Найти и нажать кнопку "меню"
            clicked = False
            for sel in options:
                try:
                    page.wait_for_selector(sel, timeout=2500)
                    page.click(sel)
                    clicked = True
                    break
                except TimeoutError:
                    continue
                except Exception:
                    continue
            if not clicked:
                # возможно меню доступно через кнопку с aria-label 'More options' в svg внутри button
                # Пытаемся кликнуть по общему селектору
                try:
                    page.click('button:has(svg[aria-label])', timeout=2500)
                    clicked = True
                except Exception:
                    pass
            if not clicked:
                print(f"Меню не найдено для {url}, пропускаю.")
                continue

            # Нажать пункт Delete (по тексту) — попробовать все языки
            deleted_clicked = False
            for txt in delete_texts:
                try:
                    page.click(f'text="{txt}"', timeout=2500)
                    deleted_clicked = True
                    break
                except TimeoutError:
                    continue
                except Exception:
                    continue

            if not deleted_clicked:
                # возможно пункт в меню имеет селектор role="menuitem" и содержит слово 'Delete' в кнопке
                try:
                    menu_items = page.query_selector_all('button,div[role="menuitem"]')
                    for mi in menu_items:
                        t = (mi.inner_text() or "").strip()
                        for token in delete_texts:
                            if token.lower() in t.lower():
                                mi.click()
                                deleted_clicked = True
                                break
                        if deleted_clicked:
                            break
                except Exception:
                    pass

            # если требует подтверждение — нажать подтверждение (по тексту)
            if deleted_clicked:
                # Подтверждающие кнопки с текстом Delete/Удалить и т.п.
                confirm_texts = ["Delete","Удалить","Sí, eliminar","Eliminar","Confirmer","OK","Да, удалить"]
                confirmed = False
                for ct in confirm_texts:
                    try:
                        page.wait_for_selector(f'text="{ct}"', timeout=2500)
                        page.click(f'text="{ct}"')
                        confirmed = True
                        break
                    except TimeoutError:
                        continue
                    except Exception:
                        continue
                # Некритично — иногда нет подтверждения
                deleted += 1
                print(f"{i}/{len(urls)} удалён.")
                random_delay(1.5, 3.0)
            else:
                print(f"Не удалось нажать Delete для {url}.")
                continue

        except Exception as e:
            p = f"logs/error_{username}_{i}.png"
            try:
                page.screenshot(path=p)
            except Exception:
                pass
            print(f"Ошибка при обработке {url}: {e}. Скрин: {p}")
            continue

    return deleted
