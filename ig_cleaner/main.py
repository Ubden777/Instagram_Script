# ig_cleaner/main.py
from playwright.sync_api import sync_playwright
from ig_cleaner.morelogin_client import MoreLoginClient
from ig_cleaner.ig_actions import delete_posts
from ig_cleaner.utils import load_env
import time


def main():
    env = load_env()

    ml = MoreLoginClient(env["ML_API_KEY"], env["ML_API_URL"])

    username = input("Instagram username (without @): ").strip()
    profile_id = input("MoreLogin profile_id: ").strip()

    count = input("How many posts to delete (default 25): ").strip()
    count = int(count) if count else 25

    dry = input("Dry-run? (y/N): ").strip().lower() == "y"

    ws = None

    try:
        print("Starting MoreLogin profile…")
        ws = ml.start_profile(profile_id)

        print("Connecting Playwright…")
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            time.sleep(1)

            deleted = delete_posts(page, username, count, dry_run=dry)
            print(f"Finished: deleted {deleted} posts")

            try:
                browser.close()
            except:
                pass

        print("\n✅ Task completed.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        print("Stopping profile…")
        ok = ml.stop_profile(profile_id)
        print("Profile stopped:", ok)


if __name__ == "__main__":
    main()
