"""
⚠️ WARNING: DO NOT MODIFY THIS FILE
This is a core framework file. Changes may break test execution.

Pytest configuration and fixtures.
"""
import os
# Disable Python bytecode generation to prevent caching issues
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import pytest
import asyncio
import allure
from typing import Dict
from playwright.async_api import Page
from utils.playwright_factory import PlaywrightFactory
from utils.common_methods import CommonMethods
from utils.logger import Log
from pages.login_page import LoginPage
from pages.landing_page import LandingPage
from pages.home_page import HomePage
from pages.working_screen_page import WorkingScreenPage
from pages.working_screen_page_audit import WorkingScreenPageAudit


@pytest.fixture(scope="class")
async def browser_setup(request):
    """
    Setup browser before each test.
    
    Args:
        request: Pytest request object
    """
    # Get browser parameter from command line or use default
    browser_name = request.config.getoption("--browser", default="chrome")
    
    # Handle if browser_name is a list (from pytest-playwright)
    if isinstance(browser_name, list):
        browser_name = browser_name[0] if browser_name else "chrome"
    
    Log.info(f"Setting up browser: {browser_name}")
    
    # Initialize PlaywrightFactory
    pf = PlaywrightFactory()
    props = pf.init_prop()
    page = await pf.init_browser(props, browser_name)
    
    # Ensure page is fully ready
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(500)
    Log.info(f"Page ready, URL: {page.url}")
    
    yield {"page": page, "props": props, "factory": pf}
    
    # Cleanup
    Log.info("Closing browser")
    await PlaywrightFactory.close_browser()


@pytest.fixture(scope="class")
async def page(browser_setup) -> Page:
    """Get the page instance."""
    return browser_setup["page"]


@pytest.fixture(scope="class")
async def config(browser_setup) -> Dict[str, str]:
    """Get configuration properties."""
    return browser_setup["props"]


@pytest.fixture(scope="class")
async def common_methods(page) -> CommonMethods:
    """Get CommonMethods instance."""
    return CommonMethods(page)


@pytest.fixture(scope="class")
async def login_page(page) -> LoginPage:
    """Get LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="class")
async def landing_page(page) -> LandingPage:
    """Get LandingPage instance."""
    return LandingPage(page)


@pytest.fixture(scope="class")
async def home_page(page) -> HomePage:
    """Get HomePage instance."""
    return HomePage(page)


@pytest.fixture(scope="class")
async def working_screen_page(page) -> WorkingScreenPage:
    """Get WorkingScreenPage instance."""
    return WorkingScreenPage(page)


@pytest.fixture(scope="class")
async def working_screen_page_audit(page) -> WorkingScreenPageAudit:
    """Get WorkingScreenPageAudit instance."""
    return WorkingScreenPageAudit(page)


@pytest.fixture(scope="class", autouse=True)
async def setup_pages(request, page, config, login_page, landing_page, home_page, 
                      working_screen_page, working_screen_page_audit, common_methods):
    """
    Automatically inject all page objects into test class instance.
    This allows tests to use self.landing_page instead of passing fixtures.
    """
    # Clear cached locators to ensure fresh load
    CommonMethods._locators.clear()
    CommonMethods._loaded_files.clear()
    Log.info("Cleared locator cache for new test class")
    
    # Store all page objects and config as class attributes
    request.cls.page = page
    request.cls.config = config
    request.cls.login_page = login_page
    request.cls.landing_page = landing_page
    request.cls.home_page = home_page
    request.cls.working_screen_page = working_screen_page
    request.cls.working_screen_page_audit = working_screen_page_audit
    request.cls.common_methods = common_methods
    
    yield


# Removed this for solving an issue in runtime.
# def pytest_addoption(parser):
#     """Add custom command line options."""
#     parser.addoption(
#         "--browser",
#         action="store",
#         default="chrome",
#         help="Browser to run tests: chrome, chromium, firefox, webkit"
#     )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        try:
            # Get page from fixture if available
            if "page" in item.funcargs:
                page = item.funcargs["page"]
                
                # Create reports directory if it doesn't exist
                import os
                if not os.path.exists("reports/screenshots"):
                    os.makedirs("reports/screenshots")
                
                # Take screenshot with timestamp
                import time
                timestamp = int(time.time() * 1000)
                screenshot_path = f"reports/screenshots/failure_{timestamp}.png"
                
                # Take screenshot using the page object directly
                asyncio.get_event_loop().run_until_complete(
                    page.screenshot(path=screenshot_path, full_page=True)
                )
                
                Log.info(f"Screenshot saved: {screenshot_path}")
                
                # Attach to allure if available
                try:
                    import allure
                    with open(screenshot_path, "rb") as image_file:
                        allure.attach(
                            image_file.read(),
                            name="Screenshot on Failure",
                            attachment_type=allure.attachment_type.PNG
                        )
                except ImportError:
                    pass  # Allure not available
                except Exception as e:
                    Log.error(f"Error attaching screenshot to allure: {e}")
        except Exception as e:
            Log.error(f"Error taking screenshot on failure: {e}")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "order: specify test execution order"
    )

