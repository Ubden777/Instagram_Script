# ig_actions.py (sync delete_posts)
import os, time, random
from playwright.sync_api import TimeoutError

def random_delay(a=1.5, b=3.0):
    time.sleep(random.uniform(a, b))

def delete_posts(page, username, count=25):
    os.makedirs("logs", exist_ok=True)
    page.goto(f"https://www.instagram.com/{username}/", wait_until="load")
    random_delay(2,4)
    if "login" in page.url:
        print("Похоже, профиль не залогинен в MoreLogin.")
        return 0

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
    for i, url in enumerate(urls, start=1):
        try:
            page.goto(url, wait_until="load")
            random_delay(1.0, 2.5)
            # try many selectors
            options = ['svg[aria-label="More options"]','button[aria-label="More options"]','svg[aria-label="Еще варианты"]','button[aria-label="Еще варианты"]']
            clicked=False
            for sel in options:
                try:
                    page.wait_for_selector(sel, timeout=2500)
                    page.click(sel)
                    clicked=True
                    break
                except TimeoutError:
                    continue
            if not clicked:
                print("Кнопка меню не найдена, пропускаю.")
                continue
            # find Delete text
            delete_texts = ["Delete","Удалить","Eliminar","Supprimer"]
            found=False
            for txt in delete_texts:
                try:
                    page.click(f'text="{txt}"', timeout=2500)
                    found=True
                    break
                except TimeoutError:
                    continue
            if not found:
                print("Кнопка 'Delete' не найдена, пропускаю.")
                continue
            # confirm
            try:
                page.click('text="Delete"', timeout=3000)
            except TimeoutError:
                try:
                    page.click('text="Удалить"', timeout=3000)
                except TimeoutError:
                    pass
            deleted +=1
            print(f"{i}/{len(urls)} удалён.")
            random_delay(1.5, 3.0)
        except Exception as e:
            p = f"logs/error_{username}_{i}.png"
            try: page.screenshot(path=p)
            except: pass
            print(f"Ошибка при {url}: {e}. Скрин: {p}")
            continue
    return deleted
