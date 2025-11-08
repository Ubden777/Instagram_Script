import os
import sys
from dotenv import load_dotenv

def load_env():
    """Loads environment variables from .env file and returns them as a dict."""
    load_dotenv()
    api_key = os.getenv('ML_API_KEY')
    api_url = os.getenv('ML_API_URL')

    if not api_key or not api_url:
        print("Ошибка: Переменные окружения ML_API_KEY и ML_API_URL не найдены.")
        print("Пожалуйста, создайте файл .env в папке ig_cleaner и добавьте в него:")
        print("ML_API_KEY=ваш_ключ")
        print("ML_API_URL=http://127.0.0.1:35000")
        sys.exit(1)

    return {"ML_API_KEY": api_key, "ML_API_URL": api_url}
