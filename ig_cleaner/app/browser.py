from playwright.async_api import async_playwright, Page
from typing import Optional
from .logging_config import get_logger

log = get_logger(__name__)

async def connect_to_browser(ws_endpoint: str) -> Optional[Page]:
    """
    Connects to a running browser instance via its remote debugging endpoint (WebSocket).
    """
    log.info("Attempting to connect to browser.", ws_endpoint=ws_endpoint)
    try:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        page = context.pages[0]
        log.info("Successfully connected to browser.")
        return page
    except Exception as e:
        log.exception("Failed to connect to browser.", ws_endpoint=ws_endpoint)
        return None
