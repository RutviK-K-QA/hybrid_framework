"""Playwright factory for browser management."""
import os
from contextvars import ContextVar
from typing import Dict, Optional
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright
)
from utils.logger import Log
from utils.common_methods import CommonMethods


class PlaywrightFactory:
    """Factory class for Playwright browser management."""

    # Context variables for async support
    _playwright_context: ContextVar[Optional[Playwright]] = ContextVar('playwright', default=None)
    _browser_context: ContextVar[Optional[Browser]] = ContextVar('browser', default=None)
    _context_context: ContextVar[Optional[BrowserContext]] = ContextVar('context', default=None)
    _page_context: ContextVar[Optional[Page]] = ContextVar('page', default=None)
    _playwright_manager = None

    def __init__(self):
        """Initialize the factory."""
        self.props: Optional[Dict[str, str]] = None

    @classmethod
    def get_playwright(cls) -> Optional[Playwright]:
        """Get the Playwright instance."""
        return cls._playwright_context.get()

    @classmethod
    def get_browser(cls) -> Optional[Browser]:
        """Get the Browser instance."""
        return cls._browser_context.get()

    @classmethod
    def get_browser_context(cls) -> Optional[BrowserContext]:
        """Get the BrowserContext instance."""
        return cls._context_context.get()

    @classmethod
    def get_page(cls) -> Optional[Page]:
        """Get the Page instance."""
        return cls._page_context.get()

    async def init_browser(self, props: Dict[str, str], browser_name: str) -> Page:
        """
        Initialize the browser.
        
        Args:
            props: Properties dictionary
            browser_name: Name of the browser to launch
            
        Returns:
            Page: The initialized page
        """
        Log.info(f"Browser Name is:: {browser_name}")

        # Start Playwright
        if self._playwright_manager is None:
            self._playwright_manager = await async_playwright().start()
        
        playwright = self._playwright_manager
        self._playwright_context.set(playwright)

        # Launch browser based on browser_name
        browser_name_lower = browser_name.lower()
        
        if browser_name_lower == "chromium":
            browser = await playwright.chromium.launch(headless=False)
        elif browser_name_lower == "firefox":
            browser = await playwright.firefox.launch(headless=False)
        elif browser_name_lower == "safari" or browser_name_lower == "webkit":
            browser = await playwright.webkit.launch(headless=False)
        elif browser_name_lower == "chrome":
            browser = await playwright.chromium.launch(
                channel="chrome",
                headless=False,
                args=['--start-maximized']  # Start Chrome in maximized mode
            )
        else:
            Log.error("Browser name is invalid....")
            raise ValueError(f"Invalid browser name: {browser_name}")

        self._browser_context.set(browser)

        # Create browser context with no viewport (uses full available space)
        context = await browser.new_context(no_viewport=True)
        self._context_context.set(context)

        page = await context.new_page()
        self._page_context.set(page)

        # Navigate to URL
        url = props.get("url", "").strip()
        Log.info(f"Navigating to URL: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        Log.info("Page loaded successfully")

        return page

    def init_prop(self) -> Dict[str, str]:
        """
        Initialize properties from config file.
        
        Returns:
            Dict[str, str]: Properties dictionary
        """
        self.props = CommonMethods.init_prop()
        return self.props

    @classmethod
    async def take_screenshot(cls) -> str:
        """
        Take a screenshot.
        
        Returns:
            str: Path to the screenshot
        """
        page = cls.get_page()
        
        if not os.path.exists("Screenshots"):
            os.makedirs("Screenshots")
        
        import time
        timestamp = int(time.time() * 1000)
        screenshot_path = f"Screenshots/{timestamp}.png"
        
        await page.screenshot(path=screenshot_path, full_page=True)
        
        return screenshot_path

    @classmethod
    async def close_browser(cls):
        """Close the browser and cleanup."""
        try:
            page = cls.get_page()
            if page:
                await page.close()
            
            context = cls.get_browser_context()
            if context:
                await context.close()
            
            browser = cls.get_browser()
            if browser:
                await browser.close()
            
            if cls._playwright_manager:
                await cls._playwright_manager.stop()
                cls._playwright_manager = None
        except Exception as e:
            Log.error(f"Error closing browser: {e}")

