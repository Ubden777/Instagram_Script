# main.py
from playwright.sync_api import sync_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.ig_actions import delete_posts
from ig_cleaner.utils import load_env
import time

def main():
    env = load_env()
    ml = MoreLoginClient(env["ML_API_KEY"], env["ML_API_URL"])
    username = input("Введите username (целевой профиль, без @): ").strip()
    profile_id = input("Введите profile_id (MoreLogin): ").strip()
    count = input("Сколько постов удалить? (по умолчанию 25): ").strip()
    count = int(count) if count else 25

    ws = None
    try:
        print("Запуск профиля MoreLogin...")
        ws = ml.start_profile(profile_id)
        if not ws:
            print("Не удалось получить WebSocket/CDP endpoint от MoreLogin.")
            return

        print("Подключение Playwright к MoreLogin (CDP)...")
        with sync_playwright() as p:
            # Подключаемся по CDP/WS
            browser = p.chromium.connect_over_cdp(ws)
            # получить существующую context (MoreLogin часто создаёт context)
            contexts = browser.contexts
            context = contexts[0] if contexts else browser.new_context()
            pages = context.pages
            page = pages[0] if pages else context.new_page()

            # optional small delay for page load stability
            time.sleep(1.0)

            deleted = delete_posts(page, username, count)
            print(f"Удалено {deleted} постов")
            try:
                browser.close()
            except Exception:
                pass

        print("Задание выполнено.")
    except Exception as e:
        print("ОШИБКА:", e)
    finally:
        # Гарантированно пытаемся остановить профиль
        try:
            ok = ml.stop_profile(profile_id)
            if ok:
                print("Профиль остановлен.")
            else:
                print("Профиль остановить не удалось (возможно, уже остановлен).")
        except Exception as e:
            print("Ошибка при остановке профиля:", e)

if __name__=='__main__':
    main()
