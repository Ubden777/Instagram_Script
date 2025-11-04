from playwright.async_api import async_playwright, Browser, Page
from typing import Optional

async def connect_to_browser(ws_endpoint: str) -> Optional[Page]:
    """
    Connects to a running browser instance via its remote debugging endpoint (WebSocket).

    Args:
        ws_endpoint: The WebSocket endpoint of the browser.

    Returns:
        The first page of the browser if connection is successful, otherwise None.
    """
    try:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        # Assuming the browser has at least one context and one page open.
        # MoreLogin usually opens a default page.
        context = browser.contexts[0]
        page = context.pages[0]
        return page
    except Exception as e:
        print(f"Failed to connect to browser: {e}")
        return None

# Example usage (for testing with a running MoreLogin profile)
async def main():
    # Replace with a real WebSocket endpoint from a running MoreLogin profile
    # You can get this by running morelogin_client.py
    test_ws_endpoint = "ws://127.0.0.1:9222/devtools/browser/your-profile-uuid"

    page = await connect_to_browser(test_ws_endpoint)

    if page:
        print("Successfully connected to the browser.")
        print(f"Page title: {await page.title()}")
        await page.goto("https://www.instagram.com")
        print(f"Navigated to Instagram. New title: {await page.title()}")

        # Keep the browser open for a bit to see the result
        await page.wait_for_timeout(10000)

        # Close the connection
        await page.context.browser.close()
        print("Browser connection closed.")
    else:
        print("Could not connect to the browser.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
