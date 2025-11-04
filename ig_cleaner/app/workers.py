import asyncio
import random
from .db import Session, Account, Deletion
from .encrypt import decrypt_data
from .morelogin_client import MoreLoginClient
from .browser import connect_to_browser
from . import ig_actions
from .config import MAX_DELETES_PER_HOUR
from .notifier import send_telegram_message
from .logging_config import get_logger, setup_logging

# Setup logging once at the start of the app
setup_logging()

async def process_account(account_id: int):
    """
    The main worker function to process a single account.
    """
    db_session = Session()
    account = db_session.query(Account).filter_by(id=account_id).first()

    # Get a logger specific to this account's username for file logging
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
            raise Exception("Failed to get WebSocket endpoint from MoreLogin.")

        page = await connect_to_browser(ws_endpoint)
        if not page:
            raise Exception("Failed to connect to the browser.")

        await page.goto("https://www.instagram.com/")
        await asyncio.sleep(5)

        is_logged_in = "login" not in await page.url()
        if not is_logged_in:
            log.info("Not logged in. Attempting to log in.")
            login_success = await ig_actions.login_to_instagram(page, account.username, password)
            if not login_success:
                raise Exception("Login failed, potential 2FA/challenge.")

        posts_to_delete = await ig_actions.get_latest_posts(page, account.username)

        if not posts_to_delete:
            log.info("No posts found to delete.")
            await send_telegram_message(f"✅ No posts to delete for `{account.username}`.")
            return

        deletions_count = 0
        consecutive_errors = 0
        for post_url in posts_to_delete:
            if deletions_count >= 25:
                break

            success = await ig_actions.delete_post(page, post_url)

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
                    log.error("Too many consecutive errors. Quarantining account.")
                    account.status = 'quarantine'
                    await send_telegram_message(f"⚠️ Account `{account.username}` quarantined due to multiple errors.")
                    break

        db_session.commit()
        log.info("Finished processing.", deleted_count=deletions_count)
        await send_telegram_message(f"✅ Successfully deleted {deletions_count} posts for `{account.username}`.")

    except Exception as e:
        log.exception("An error occurred while processing account.", account_username=account.username)
        account.status = 'quarantine'
        db_session.commit()
        await send_telegram_message(f"🚨 ERROR for `{account.username}`: {e}. Account quarantined.")

    finally:
        if ws_endpoint:
            log.info("Stopping MoreLogin profile.", profile_id=account.profile_id)
            ml_client.stop_profile(account.profile_id)

        db_session.close()
        log.info("Worker finished.", account_id=account_id)
