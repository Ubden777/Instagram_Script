import os
from dotenv import load_dotenv

def load_env():
    """
    Загружает переменные окружения из .env файла.
    Возвращает словарь с переменными или None, если файл или переменные отсутствуют.
    """
    # .env файл может находиться в корне проекта, а не внутри ig_cleaner
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(dotenv_path):
        dotenv_path = '.env' # Или ищем в текущей директории

    if not os.path.exists(dotenv_path):
        print("Ошибка: Файл .env не найден.")
        print("Пожалуйста, создайте файл .env в корневой папке проекта по примеру .env.example")
        return None

    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv('ML_API_KEY')
    api_url = os.getenv('ML_API_URL')

    if not api_key or not api_url:
        print("Ошибка: Переменные окружения ML_API_KEY и ML_API_URL не найдены в .env файле.")
        print("Пожалуйста, убедитесь, что они заданы.")
        return None

    return {"ML_API_KEY": api_key, "ML_API_URL": api_url}
