from playwright.sync_api import sync_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.ig_actions import delete_posts
from ig_cleaner.utils import load_env, random_delay

def main():
    username = input("Введите имя пользователя Instagram: ")
    profile_id = input("Введите ID профиля MoreLogin: ")
    count = int(input("Сколько последних постов удалить? (по умолчанию 25): ") or 25)

    api_key, api_url = load_env()
    ml = MoreLoginClient(api_key, api_url)
    ws = ml.start_profile(profile_id)
    if not ws:
        print("❌ Не удалось получить WebSocket endpoint")
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        try:
            delete_posts(page, username, count)
            print(f"✅ Удалено {count} постов для {username}")
        except Exception as e:
            print("⚠️ Ошибка:", e)
        finally:
            ml.stop_profile(profile_id)
            browser.close()

if __name__ == "__main__":
    main()
