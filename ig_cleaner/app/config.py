import os

# MoreLogin API Key
ML_API_KEY = os.getenv("ML_API_KEY")

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Database URL
DB_URL = os.getenv("DB_URL", "sqlite:///data/accounts.db")

# Encryption Key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Deletion Settings
DEFAULT_DELETE_COUNT = int(os.getenv("DEFAULT_DELETE_COUNT", 25))
MAX_DELETES_PER_HOUR = int(os.getenv("MAX_DELETES_PER_HOUR", 8))

# Worker Settings
WORKERS_COUNT = int(os.getenv("WORKERS_COUNT", 3))

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# Default log directory in the user's home folder for cross-platform compatibility
DEFAULT_LOG_DIR = os.path.join(os.path.expanduser("~"), ".ig_cleaner", "logs")
LOG_DIR = os.getenv("LOG_DIR", DEFAULT_LOG_DIR)
