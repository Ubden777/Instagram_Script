import asyncio
import random
import os
import time
from .db import Session, Account, Deletion
from .encrypt import decrypt_data
from .morelogin_client import MoreLoginClient
from .browser import connect_to_browser
from . import ig_actions
from .config import LOG_DIR
from .notifier import send_telegram_message
from .logging_config import get_logger, setup_logging

setup_logging()

def get_screenshot_path(account_username: str, action: str) -> str:
    """Generates a unique path for storing a screenshot."""
    ts = int(time.time())
    filename = f"{action}_{ts}.png"
    path = os.path.join(LOG_DIR, account_username, "screenshots")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)

async def process_account(account_id: int):
    """The main worker function to process a single account."""
    db_session = Session()
    account = db_session.query(Account).filter_by(id=account_id).first()

    log = get_logger(__name__, account_username=account.username if account else f"unknown_account_{account_id}")
    log.info("Starting worker for account.", account_id=account_id)

    if not account or not account.enabled:
        log.warning("Account is disabled or not found. Skipping.", account_id=account_id)
        db_session.close()
        return

    password = decrypt_data(account.password_encrypted)
    ml_client = MoreLoginClient()

    ws_endpoint = None
    try:
        log.info("Starting MoreLogin profile.", profile_id=account.profile_id)
        ws_endpoint = ml_client.start_profile(account.profile_id)
        if not ws_endpoint:
            raise Exception("Failed to get WebSocket endpoint.")

        page = await connect_to_browser(ws_endpoint)
        if not page:
            raise Exception("Failed to connect to the browser.")

        await page.goto("https://www.instagram.com/")
        await asyncio.sleep(5)

        if "login" in await page.url():
            log.info("Not logged in. Attempting to log in.")
            screenshot_path = get_screenshot_path(account.username, "login_failed")
            login_success = await ig_actions.login_to_instagram(page, account.username, password, screenshot_path)
            if not login_success:
                raise Exception(f"Login failed. Screenshot saved to: {screenshot_path}")

        screenshot_path = get_screenshot_path(account.username, "get_posts_failed")
        posts_to_delete = await ig_actions.get_latest_posts(page, account.username, screenshot_path=screenshot_path)

        if not posts_to_delete:
            log.info("No posts found to delete.")
            await send_telegram_message(f"✅ No posts to delete for `{account.username}`.")
            return

        deletions_count = 0
        consecutive_errors = 0
        for post_url in posts_to_delete:
            if deletions_count >= 25:
                break

            screenshot_path = get_screenshot_path(account.username, "delete_failed")
            success = await ig_actions.delete_post(page, post_url, screenshot_path=screenshot_path)

            status = "success" if success else "failed"
            log.info("Deletion attempt.", post_url=post_url, status=status)
            new_deletion = Deletion(account_id=account.id, media_id=post_url.split('/')[-2], status=status)
            db_session.add(new_deletion)

            if success:
                deletions_count += 1
                consecutive_errors = 0
                delay = random.uniform(30, 90)
                log.info(f"Waiting for {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    msg = f"⚠️ Account `{account.username}` quarantined due to multiple errors. Last error screenshot: {screenshot_path}"
                    log.error(msg)
                    account.status = 'quarantine'
                    await send_telegram_message(msg)
                    break

        db_session.commit()
        log.info("Finished processing.", deleted_count=deletions_count)
        await send_telegram_message(f"✅ Successfully deleted {deletions_count} posts for `{account.username}`.")

    except Exception as e:
        log.exception("An uncaught error occurred while processing account.", account_username=account.username)

        # Try to take a final screenshot for context
        screenshot_path = get_screenshot_path(account.username, "uncaught_exception")
        error_message = f"🚨 Uncaught ERROR for `{account.username}`: {e}. Account quarantined."

        try:
            # Check if the 'page' object exists and is usable
            if 'page' in locals() and page and not page.is_closed():
                await page.screenshot(path=screenshot_path)
                log.info("Saved screenshot of uncaught exception.", path=screenshot_path)
                error_message += f" Screenshot: `{screenshot_path}`"
        except Exception as screenshot_e:
            log.error("Failed to take screenshot during exception handling.", exc_info=screenshot_e)

        account.status = 'quarantine'
        db_session.commit()
        await send_telegram_message(error_message)

    finally:
        if ws_endpoint:
            log.info("Stopping MoreLogin profile.", profile_id=account.profile_id)
            ml_client.stop_profile(account.profile_id)

        db_session.close()
        log.info("Worker finished.", account_id=account_id)
