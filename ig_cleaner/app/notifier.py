import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .logging_config import get_logger

log = get_logger(__name__)

def send_telegram_message(message: str):
    """
    Sends a message to the configured Telegram chat.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram token or chat ID is not configured. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            log.info("Telegram notification sent successfully.")
            return True
        else:
            log.error("Failed to send Telegram notification.", status_code=response.status_code, response_text=response.text)
            return False
    except requests.exceptions.RequestException as e:
        log.exception("An error occurred while sending Telegram notification.")
        return False
