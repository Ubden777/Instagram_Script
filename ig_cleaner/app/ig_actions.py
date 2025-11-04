import asyncio
import random
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .config import DEFAULT_DELETE_COUNT

async def login_to_instagram(page: Page, username: str, password: str):
    """
    Handles the login process for Instagram.
    """
    print(f"Attempting to log in as {username}...")
    try:
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_selector('input[name="username"]', timeout=10000)

        await page.fill('input[name="username"]', username)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await page.fill('input[name="password"]', password)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await page.click('button[type="submit"]')

        # Wait for either the home page to load or a challenge screen
        await page.wait_for_url("https://www.instagram.com/", timeout=15000)
        print("Login successful.")
        return True
    except PlaywrightTimeoutError:
        print("Login failed or a 2FA/challenge was encountered.")
        # In a real scenario, we'd save a screenshot here and quarantine the account.
        return False
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        return False

async def get_latest_posts(page: Page, username: str, count: int = DEFAULT_DELETE_COUNT):
    """
    Navigates to the user's profile and collects the URLs of the latest posts.
    """
    print(f"Fetching the latest {count} posts for {username}...")
    profile_url = f"https://www.instagram.com/{username}/"
    await page.goto(profile_url)

    post_urls = []
    try:
        await page.wait_for_selector('a[href*="/p/"]', timeout=15000)

        # This is a simple way to get posts, might need to scroll for more
        links = await page.query_selector_all('a[href*="/p/"]')
        for link in links:
            href = await link.get_attribute('href')
            if href and href not in post_urls:
                post_urls.append(f"https://www.instagram.com{href}")
            if len(post_urls) >= count:
                break

        print(f"Found {len(post_urls)} posts.")
        return post_urls[:count]
    except PlaywrightTimeoutError:
        print("Could not find any posts on the profile page.")
        return []
    except Exception as e:
        print(f"An error occurred while fetching posts: {e}")
        return []

async def delete_post(page: Page, post_url: str):
    """
    Navigates to a post, opens the options menu, and deletes the post.
    This function contains critical selectors that are likely to change.
    """
    print(f"Attempting to delete post: {post_url}")
    try:
        await page.goto(post_url)

        # Selector for the three-dots menu icon. This is highly unstable.
        # Instagram uses SVGs and complex class names. Using aria-label is more robust.
        options_button_selector = 'svg[aria-label="More options"]'
        await page.wait_for_selector(options_button_selector, timeout=10000)
        await page.click(options_button_selector)
        await asyncio.sleep(random.uniform(1.2, 2.5))

        # Selector for the "Delete" button in the menu.
        # Using text is good, but depends on the UI language.
        delete_button_selector = 'text="Delete"'
        await page.click(delete_button_selector)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Selector for the final confirmation "Delete" button in the dialog.
        confirm_delete_selector = 'button:has-text("Delete")'
        await page.wait_for_selector(confirm_delete_selector, timeout=5000)
        await page.click(confirm_delete_selector)

        # Wait for a success indicator, like the post disappearing or a banner.
        # For now, we'll just wait for a moment.
        await page.wait_for_timeout(5000)

        print(f"Successfully deleted post: {post_url}")
        return True
    except PlaywrightTimeoutError as e:
        print(f"A timeout occurred while trying to delete {post_url}. The UI might have changed. Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during deletion of {post_url}: {e}")
        return False
