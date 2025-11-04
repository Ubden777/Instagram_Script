import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message: str):
    """
    Sends a message to the configured Telegram chat.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token or chat ID is not configured. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram notification sent successfully.")
            return True
        else:
            print(f"Failed to send Telegram notification. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending Telegram notification: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # This requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to be set
    send_telegram_message("This is a test message from the *IG Cleaner* script.")
