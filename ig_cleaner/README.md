# IG Cleaner

A Python script for automatically deleting the latest N posts from Instagram accounts on a schedule. This tool uses Playwright for browser automation and an anti-detect browser (MoreLogin) to minimize the risk of account blocks.

## Features

-   **Scheduled Deletion**: Deletes the last N posts (default 25) from specified Instagram accounts.
-   **Anti-Detect Integration**: Uses MoreLogin to manage browser profiles and proxies, reducing detection risk.
-   **Safety First**: Implements human-like delays, error handling, and an account quarantine system.
-   **Notifications**: Sends real-time alerts to Telegram for successes, errors, and warnings.
-   **Secure**: Encrypts all sensitive credentials (passwords, proxies) at rest.
-   **Parallel Execution**: Can process multiple accounts simultaneously.

## Technical Stack

-   **Python 3.10+**
-   **Playwright**: For robust browser automation.
-   **MoreLogin**: For managing anti-detect browser profiles.
-   **APScheduler**: For scheduling jobs.
-   **SQLAlchemy**: For database interaction (SQLite).
-   **Cryptography**: For AES encryption of credentials.
-   **Structlog**: For structured and file-based logging.

## Setup and Installation

### 1. Prerequisites

-   Python 3.10 or higher.
-   The MoreLogin application installed and running on your Windows machine.
-   A MoreLogin account with an API key.
-   A Telegram Bot and a Chat ID for notifications.

### 2. Clone the Repository

```bash
git clone <repository_url>
cd ig_cleaner
```

### 3. Install Dependencies

It is highly recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
playwright install  # Installs browser binaries
```

### 4. Configure Environment Variables

Create a `.env` file in the `ig_cleaner` root directory and add the following variables. The script will load these automatically if `python-dotenv` is installed, or you can set them in your system.

```env
# MoreLogin API Key
ML_API_KEY="your_morelogin_api_key"

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_telegram_chat_id"

# Encryption Key (MUST be a 32-character string)
ENCRYPTION_KEY="your_generated_32_character_secret_key"

# Optional: Override default settings
# DB_URL="sqlite:///data/accounts.db"
# DEFAULT_DELETE_COUNT="25"
# WORKERS_COUNT="3"
# LOG_DIR="C:/path/to/your/logs" # Use a Windows-compatible path
```
**Security Note**: The `ENCRYPTION_KEY` is critical for securing your account passwords. It **must be exactly 32 characters (bytes) long**. Using a key of any other length will cause the application to fail.

You can generate a secure, random key with the following command:

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```
Copy the output of this command and paste it as the value for `ENCRYPTION_KEY`. Keep this key safe and do not commit it to version control.

## Usage

### 1. Initialize the Database

First, create the SQLite database and its tables.

```bash
python manage_accounts.py initdb
```
This will create a `data/` directory with the `accounts.db` file inside.

### 2. Add an Account

Use the CLI to add an Instagram account to the database. You will be prompted to enter the password securely.

```bash
python manage_accounts.py add --username "your_ig_username" --profile-id "your_morelogin_profile_id" --proxy "http://user:pass@host:port"
```
-   `--username`: Your Instagram login username.
-   `--profile-id`: The Profile ID from your MoreLogin application.
-   `--proxy`: The proxy associated with this profile.

### 3. (Optional) Add a Schedule

You can add schedules directly to the `schedules` table in the `accounts.db` file using a SQLite browser.

-   `cron_expr`: A cron expression (e.g., `0 3 * * *` for 3 AM daily).
-   `target_account_ids`: A comma-separated list of account IDs, or `all`.

### 4. Run the Scheduler

To start the main application and begin processing jobs, run:

```bash
python -m app.main
```

The scheduler will load the jobs from the database and run them at the specified times.

## Account Management CLI

The `manage_accounts.py` script provides a few commands:

-   **`add`**: Add a new account.
-   **`update`**: Update an existing account's profile ID, proxy, or password.
-   **`list`**: List all accounts currently in the database.
-   **`initdb`**: Initialize the database.

Example:
```bash
python manage_accounts.py list
python manage_accounts.py update --username "your_ig_username" --proxy "http://new_proxy"
```

## Logging

-   The script prints structured logs to the console.
-   It also creates detailed logs in the directory specified by the `LOG_DIR` environment variable, with a separate subdirectory for each account. This is essential for debugging.
