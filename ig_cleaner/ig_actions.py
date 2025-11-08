# ig_cleaner/ig_actions.py
import time
import random
import os
from playwright.sync_api import TimeoutError


def random_sleep(a=1.5, b=3.0):
    time.sleep(random.uniform(a, b))


def collect_posts(page, username, limit=25):
    page.goto(f"https://www.instagram.com/{username}/", wait_until="load")
    random_sleep(2, 4)

    links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    urls = []

    for a in links:
        href = a.get_attribute("href")
        if not href:
            continue
        full = href if href.startswith("http") else f"https://www.instagram.com{href}"
        if full not in urls:
            urls.append(full)
        if len(urls) >= limit:
            break

    return urls


def delete_posts(page, username, count=25, dry_run=False):
    """
    Deletes 'count' latest posts on page 'username'.
    If dry_run=True — does NOT delete, only lists posts.
    """
    os.makedirs("logs", exist_ok=True)

    urls = collect_posts(page, username, count)
    if dry_run:
        print("\n[DRY-RUN] Posts found:")
        for u in urls:
            print(u)
        print("\nDry-run mode — no deletion performed.")
        return 0

    if not urls:
        print("No posts found.")
        return 0

    menu_selectors = [
        'svg[aria-label="More options"]',
        'button[aria-label="More options"]',
        'svg[aria-label="Опции"]',
        'button[aria-label="Опции"]',
        'svg[aria-label="Еще варианты"]',
        'button[aria-label="Еще варианты"]',
        'button:has(svg[aria-label])',
        'div[role="button"][aria-haspopup="menu"]'
    ]

    delete_texts = [
        "Delete", "Удалить", "Eliminar", "Supprimer", "Удалите публикацию", "Löschen", "Deletar"
    ]

    confirm_texts = [
        "Delete", "Удалить", "OK", "Да", "Confirm", "Sí", "Eliminar"
    ]

    deleted = 0

    for i, url in enumerate(urls, start=1):
        try:
            page.goto(url, wait_until="load")
            random_sleep(1, 2)

            clicked = False
            for sel in menu_selectors:
                try:
                    page.click(sel, timeout=2500)
                    clicked = True
                    break
                except:
                    pass

            if not clicked:
                print(f"No menu for {url}")
                continue

            deletion_clicked = False
            for txt in delete_texts:
                try:
                    page.get_by_text(txt, exact=False).click(timeout=2500)
                    deletion_clicked = True
                    break
                except:
                    pass

            if not deletion_clicked:
                print(f"No 'delete' menu item for {url}")
                continue

            confirmed = False
            for txt in confirm_texts:
                try:
                    page.get_by_text(txt, exact=False).click(timeout=2000)
                    confirmed = True
                    break
                except:
                    pass

            deleted += 1
            print(f"Deleted {i}/{len(urls)}")
            random_sleep()

        except Exception as e:
            screenshot = f"logs/error_{username}_{i}.png"
            try:
                page.screenshot(path=screenshot)
            except:
                pass
            print(f"Error on {url}: {e} (screenshot {screenshot})")

    return deleted
