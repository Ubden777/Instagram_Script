import csv
import os
from datetime import datetime

class CSVLogger:
    def __init__(self, username):
        self.username = username
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(self.log_dir, f"report_{self.username}_{timestamp}.csv")

        self.header = [
            "timestamp", "username", "post_url", "status", "attempts",
            "delete_action", "error_message", "screenshot_path", "dry_run"
        ]

        with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

        print(f"CSV-отчет будет сохранен в: {self.filepath}")

    def log(self, post_url, status, attempts=0, delete_action='n/a', error_message='', screenshot_path='', dry_run=False):
        """Записывает одну строку в CSV-отчет."""
        timestamp = datetime.now().isoformat()
        row = [
            timestamp, self.username, post_url, status, attempts,
            delete_action, error_message, screenshot_path, dry_run
        ]

        try:
            with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось записать в CSV-файл {self.filepath}. Ошибка: {e}")
