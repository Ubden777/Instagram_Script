# main.py (sync, с finally)
# main.py (sync)
from playwright.sync_api import sync_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.ig_actions import delete_posts
from ig_cleaner.utils import load_env

def main():
    env = load_env()
    ml = MoreLoginClient(env["ML_API_KEY"], env["ML_API_URL"])
    username = input("Введите username: ").strip()
    profile_id = input("Введите profile_id: ").strip()
    count = input("Сколько постов удалить? (25): ").strip()
    count = int(count) if count else 25

    ws = None
    try:
        print("Запуск профиля MoreLogin...")
        ws = ml.start_profile(profile_id)
        if not ws:
            print("Не удалось получить ws endpoint.")
            return

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws)
            contexts = browser.contexts
            context = contexts[0] if contexts else browser.new_context()
            pages = context.pages
            page = pages[0] if pages else context.new_page()
            deleted = delete_posts(page, username, count)
            print(f"Удалено {deleted} постов")
            browser.close()
    except Exception as e:
        print("ОШИБКА:", e)
    finally:
        try:
            ml.stop_profile(profile_id)
            print("Профиль остановлен")
        except Exception as e:
            print("Ошибка при остановке профиля:", e)

if __name__=='__main__':
    main()
