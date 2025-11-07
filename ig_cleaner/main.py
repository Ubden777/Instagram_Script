# main.py (заменить содержимое на это)
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

    username = input("Введите username: ").strip()
    profile_id = input("Введите profile_id: ").strip()
    try:
        count_str = input("Введите количество постов для удаления (по умолчанию 25): ").strip()
        delete_count = int(count_str) if count_str else 25
    except ValueError:
        print("Некорректное число. Используется значение по умолчанию: 25")
        delete_count = 25

    ml_client = MoreLoginClient(api_key, api_url)

    ws_endpoint = None
    try:
        print("Запуск профиля MoreLogin...")
        ws_endpoint = ml_client.start_profile(profile_id)
        if not ws_endpoint:
            print("Не удалось получить endpoint от MoreLogin. Проверьте profile_id и ML_API_URL/ML_API_KEY.")
            return

        print("Подключение к браузеру через CDP...")
        # Подключаем Playwright к уже запущенному MoreLogin-браузеру
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(ws_endpoint)
        # получаем контекст и страницу
        contexts = browser.contexts
        if not contexts:
            context = await browser.new_context()
        else:
            context = contexts[0]
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        # Выполнить удаление
        actually_deleted = await delete_posts(page, username, delete_count)

        # Закрываем подключение к браузеру
        await browser.close()
        await playwright.stop()
        print(f"✅ Готово! Удалено {actually_deleted} постов у {username}")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    finally:
        if profile_id:
            print("Завершение работы и остановка профиля...")
            try:
                ml_client.stop_profile(profile_id)
            except Exception as ex:
                print(f"Ошибка при остановке профиля: {ex}")

if __name__ == "__main__":
    asyncio.run(main())
