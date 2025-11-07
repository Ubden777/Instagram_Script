import asyncio
from playwright.async_api import async_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.utils import load_environment_variables
from ig_cleaner.ig_actions import delete_posts

async def main():
    """
    Main function to run the Instagram cleaner script.
    """
    api_key, api_url = load_environment_variables()

    username = input("Введите username: ")
    profile_id = input("Введите profile_id: ")
    try:
        count_str = input("Введите количество постов для удаления (по умолчанию 25): ")
        delete_count = int(count_str) if count_str else 25
    except ValueError:
        print("Некорректный ввод. Будет удалено 25 постов.")
        delete_count = 25

    ml_client = MoreLoginClient(api_key, api_url)
    ws_endpoint = None

    try:
        print("Запуск профиля MoreLogin...")
        ws_endpoint = ml_client.start_profile(profile_id)
        if not ws_endpoint:
            print("Не удалось запустить профиль. Проверьте API ключ и ID профиля.")
            return

        print("Подключение к браузеру...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()

            actually_deleted = await delete_posts(page, username, delete_count)

            await browser.close()
            print(f"✅ Готово! Удалено {actually_deleted} постов у {username}")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    finally:
        if profile_id:
            print("Завершение работы и остановка профиля...")
            ml_client.stop_profile(profile_id)

if __name__ == "__main__":
    asyncio.run(main())
