from playwright.sync_api import sync_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.ig_actions import delete_posts
from ig_cleaner.utils import load_env
from ig_cleaner.logger import CSVLogger
import sys

def main():
    # 1. Загрузка окружения
    env = load_env()
    if not env:
        sys.exit(1) # Сообщение об ошибке уже выведено в load_env

    # 2. Получение данных от пользователя
    username = input("Введите username (целевой профиль, без @): ").strip()
    profile_id = input("Введите profile_id (MoreLogin): ").strip()
    count_str = input("Сколько постов удалить? (по умолчанию 25): ").strip()
    count = int(count_str) if count_str else 25
    dry_run = input("Dry-run? (y/N): ").strip().lower() == "y"

    # 3. Инициализация логгера
    logger = CSVLogger(username)

    ml_client = MoreLoginClient(env["ML_API_KEY"], env["ML_API_URL"])
    ws_endpoint = None

    try:
        # 4. Запуск профиля MoreLogin
        print("Запуск профиля MoreLogin...")
        ws_endpoint = ml_client.start_profile(profile_id)

        # 5. Подключение Playwright и проверки
        print("Подключение Playwright к MoreLogin (CDP)...")
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_endpoint)

            # Проверка на наличие контекста
            if not browser.contexts:
                raise RuntimeError("Не найдено активных браузерных контекстов в профиле MoreLogin.")

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            # 6. Выполнение основной логики
            deleted_count = delete_posts(page, logger, username, count, dry_run=dry_run)

            print(f"\n✅ Задание выполнено. Обработано постов: {deleted_count}")
            print(f"Полный отчет сохранен в: {logger.filepath}")

    except Exception as e:
        error_message = str(e).split('\n')[0]
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {error_message}")
        logger.log(post_url='n/a', status='error', error_message=f"Critical error in main: {error_message}", dry_run=dry_run)
        sys.exit(1)

    finally:
        # 7. Гарантированная остановка профиля
        if profile_id:
            print("Остановка профиля MoreLogin...")
            ml_client.stop_profile(profile_id)
            print("Профиль остановлен.")

if __name__ == '__main__':
    main()
