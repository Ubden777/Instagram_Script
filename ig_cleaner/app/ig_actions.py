import asyncio
import random
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from typing import Optional

from .config import DEFAULT_DELETE_COUNT
from .logging_config import get_logger

log = get_logger(__name__)

async def login_to_instagram(page: Page, username: str, password: str, screenshot_path: Optional[str] = None) -> bool:
    """Handles the login process for Instagram, taking a screenshot on failure."""
    log.info("Attempting to log in.", username=username)
    try:
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_selector('input[name="username"]', timeout=10000)

        await page.fill('input[name="username"]', username)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await page.fill('input[name="password"]', password)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await page.click('button[type="submit"]')

        await page.wait_for_url("https://www.instagram.com/", timeout=15000)
        log.info("Login successful.", username=username)
        return True
    except (PlaywrightTimeoutError, Exception) as e:
        log.error("Login failed or a 2FA/challenge was encountered.", username=username, error=e)
        if screenshot_path:
            await page.screenshot(path=screenshot_path)
            log.info("Saved screenshot of login failure.", path=screenshot_path)
        return False

async def get_latest_posts(page: Page, username: str, count: int = DEFAULT_DELETE_COUNT, screenshot_path: Optional[str] = None) -> list:
    """Navigates to the user's profile and collects post URLs, taking a screenshot on failure."""
    log.info(f"Fetching the latest posts.", count=count, username=username)
    profile_url = f"https://www.instagram.com/{username}/"
    await page.goto(profile_url)

    post_urls = []
    try:
        await page.wait_for_selector('a[href*="/p/"]', timeout=15000)

        links = await page.query_selector_all('a[href*="/p/"]')
        for link in links:
            href = await link.get_attribute('href')
            if href and href not in post_urls:
                post_urls.append(f"https://www.instagram.com{href}")
            if len(post_urls) >= count:
                break

        log.info(f"Found posts.", count=len(post_urls), username=username)
        return post_urls[:count]
    except (PlaywrightTimeoutError, Exception) as e:
        log.error("Could not find any posts on the profile page.", username=username, error=e)
        if screenshot_path:
            await page.screenshot(path=screenshot_path)
            log.info("Saved screenshot of post fetching failure.", path=screenshot_path)
        return []

async def delete_post(page: Page, post_url: str, screenshot_path: Optional[str] = None) -> bool:
    """Deletes a post, taking a screenshot on failure."""
    log.info("Attempting to delete post.", post_url=post_url)
    try:
        await page.goto(post_url)

        options_button_selector = 'svg[aria-label="More options"]'
        await page.wait_for_selector(options_button_selector, timeout=10000)
        await page.click(options_button_selector)
        await asyncio.sleep(random.uniform(1.2, 2.5))

        delete_button_selector = 'text="Delete"'
        await page.click(delete_button_selector)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        confirm_delete_selector = 'button:has-text("Delete")'
        await page.wait_for_selector(confirm_delete_selector, timeout=5000)
        await page.click(confirm_delete_selector)

        await page.wait_for_timeout(5000)

        log.info("Successfully deleted post.", post_url=post_url)
        return True
    except (PlaywrightTimeoutError, Exception) as e:
        log.error("A timeout or error occurred while trying to delete post.", post_url=post_url, error=e)
        if screenshot_path:
            await page.screenshot(path=screenshot_path)
            log.info("Saved screenshot of deletion failure.", path=screenshot_path)
        return False
