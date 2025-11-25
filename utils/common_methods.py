"""Common utility methods for the framework."""
import csv
import os
from pathlib import Path
from typing import Dict, Optional
from jproperties import Properties
from playwright.async_api import Page
import pyotp
from utils.logger import Log


class AllureHelper:
    """Helper class for Allure reporting."""
    
    @staticmethod
    def before(message: str, name: str = "Test Info"):
        """
        Attach text information to Allure report before test execution.
        
        Args:
            message: The message to attach
            name: The attachment name (default: "Test Info")
        """
        try:
            import allure
            allure.attach(
                message,
                name=name,
                attachment_type=allure.attachment_type.TEXT
            )
        except ImportError:
            pass  # Allure not available, skip
    
    @staticmethod
    def after(message: str):
        """
        Attach test result to Allure report after test execution.
        
        Args:
            message: The result message to attach
        """
        allure.before(message, name="Test Result")


# Alias for consistent usage across the framework
allure = AllureHelper


class CommonMethods:
    """Common methods for framework operations."""

    _page: Optional[Page] = None
    _props: Optional[Properties] = None
    _locators: Dict[str, str] = {}
    _loaded_files: set = set()

    def __init__(self, page: Page):
        """Initialize with page instance."""
        Log.info("CommonMethods constructor")
        CommonMethods._page = page

    @staticmethod
    async def take_screenshot() -> str:
        """
        Take a screenshot of the current page.
        
        Returns:
            str: Path to the screenshot file
        """
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        timestamp = int(Path(os.getcwd()).stat().st_mtime * 1000)
        screenshot_path = f"reports/{timestamp}.png"
        
        try:
            await CommonMethods._page.screenshot(path=screenshot_path, full_page=True)
        except Exception as e:
            Log.error(f"Error taking screenshot: {e}")
        
        return screenshot_path

    @staticmethod
    def init_prop() -> Dict[str, str]:
        """
        Initialize properties from config file.
        
        Returns:
            Dict[str, str]: Properties dictionary
        """
        config_path = "./configs/config.properties"
        props = Properties()
        
        try:
            with open(config_path, 'rb') as config_file:
                props.load(config_file)
            
            # Convert to dictionary
            props_dict = {}
            for key, value in props.items():
                props_dict[key] = value.data
            
            CommonMethods._props = props_dict
            return props_dict
        except FileNotFoundError:
            Log.error(f"Config file not found: {config_path}")
            return {}
        except Exception as e:
            Log.error(f"Error loading properties: {e}")
            return {}

    @staticmethod
    def get_values_from_csv(element_name: str, file_name: str) -> Optional[str]:
        """
        Retrieve value from CSV file.
        
        Args:
            element_name: Name of the element
            file_name: Name of the CSV file
            
        Returns:
            str: Locator value or None
        """
        locator = None
        
        if file_name in CommonMethods._loaded_files:
            Log.info(f"Locators already loaded for {file_name}")
        else:
            CommonMethods._locators.update(CommonMethods._load_csv(file_name))
            CommonMethods._loaded_files.add(file_name)
        
        if element_name in CommonMethods._locators:
            locator = CommonMethods._locators[element_name]
        else:
            Log.info(f"Element '{element_name}' not found in the file.")
            Log.info(f"Available keys in _locators: {list(CommonMethods._locators.keys())[:10]}")
        
        return locator

    @staticmethod
    def update_locator(element_name: str, locator: str, file_name: str):
        """
        Update or add a locator.
        
        Args:
            element_name: Name of the element
            locator: Locator value
            file_name: Name of the CSV file
        """
        CommonMethods._locators = CommonMethods._load_csv(file_name)
        
        if element_name in CommonMethods._locators:
            Log.info(f"Updating locator for element: {element_name}")
        else:
            Log.info(f"Adding new element: {element_name}")
        
        CommonMethods._locators[element_name] = locator
        CommonMethods._save_locators(CommonMethods._locators, file_name)

    @staticmethod
    def _save_locators(locators: Dict[str, str], file_name: str):
        """
        Save locators back to the CSV file.
        
        Args:
            locators: Dictionary of locators
            file_name: Name of the CSV file
        """
        csv_file = f"./object_repository/{file_name}"
        
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Element Name", "Locator"])
                
                for key, value in locators.items():
                    writer.writerow([key, value])
            
            Log.info("Locators saved successfully.")
        except Exception as e:
            Log.error(f"Error writing to the file: {e}")

    @staticmethod
    def _load_csv(file_name: str) -> Dict[str, str]:
        """
        Load CSV file.
        
        Args:
            file_name: Name of the CSV file
            
        Returns:
            Dict[str, str]: Dictionary of locators
        """
        csv_file = f"./object_repository/{file_name}"
        locators = {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    key = row.get("Element Name", "").strip()
                    value = row.get("Locator", "").strip()
                    
                    if key and value:
                        # Always add/update locators from CSV
                        locators[key] = value
            
            Log.info(f"Locators loaded successfully. Loaded {len(locators)} locators from {file_name}")
            if locators:
                Log.info(f"Sample locator keys: {list(locators.keys())[:5]}")
        except FileNotFoundError:
            Log.error(f"CSV file not found: {csv_file}")
        except Exception as e:
            Log.error(f"Error reading the file: {e}")
        
        return locators

    @staticmethod
    def generate_totp_code(secret: str) -> str:
        """
        Generate TOTP code from secret key.
        
        Args:
            secret: Base32 encoded secret key
            
        Returns:
            str: 6-digit TOTP code
        """
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            Log.info(f"Generated TOTP code: {code}")
            return code
        except Exception as e:
            Log.error(f"Error generating TOTP code: {e}")
            raise

    @staticmethod
    async def validate_text(page: Page, csv_key: str, expected: str, csv_file: str, timeout: int = 5000) -> bool:
        """
        Validate element text matches expected value.
        
        Args:
            page: Playwright page object
            csv_key: CSV key for locator
            expected: Expected text value
            csv_file: CSV filename constant
            timeout: Wait timeout in ms
        
        Returns:
            bool: True if validation passes
        
        Raises:
            AssertionError: If text doesn't match
        """
        locator = CommonMethods.get_values_from_csv(csv_key, csv_file)
        await page.wait_for_selector(locator, timeout=timeout)
        actual = (await page.text_content(locator)).strip()
        actual = actual.replace('\u00a0', ' ')  # Clean non-breaking spaces
        
        Log.info(f"Validating {csv_key}: expected='{expected}', actual='{actual}'")
        assert actual == expected, f"Text mismatch for {csv_key}: expected '{expected}', got '{actual}'"
        allure.after(f"✓ Validated {csv_key}: {expected}")
        return True

    @staticmethod
    async def validate_popup(page: Page, expected_title: str, expected_message: str, csv_file: str, timeout: int = 5000) -> bool:
        """
        Validate popup/dialog title and message.
        
        Args:
            page: Playwright page object
            expected_title: Expected popup title
            expected_message: Expected popup message
            csv_file: CSV filename constant
            timeout: Wait timeout in ms
        
        Returns:
            bool: True if validation passes
        
        Raises:
            AssertionError: If title or message doesn't match
        """
        # Validate title
        title_locator = CommonMethods.get_values_from_csv("lbl_DialogTitle", csv_file)
        await page.wait_for_selector(title_locator, timeout=timeout)
        actual_title = (await page.text_content(title_locator)).strip()
        assert actual_title == expected_title, f"Popup title mismatch: expected '{expected_title}', got '{actual_title}'"
        
        # Validate message
        msg_locator = CommonMethods.get_values_from_csv("lbl_DialogText", csv_file)
        actual_msg = (await page.text_content(msg_locator)).strip()
        assert actual_msg == expected_message, f"Popup message mismatch: expected '{expected_message}', got '{actual_msg}'"
        
        Log.info(f"✓ Popup validated: '{actual_title}' - '{actual_msg}'")
        allure.after(f"✓ Popup: {expected_title}")
        return True

    @staticmethod
    async def validate_list_options(page: Page, csv_key: str, expected_options: list, csv_file: str, timeout: int = 5000) -> bool:
        """
        Validate dropdown/list options match expected array.
        
        Args:
            page: Playwright page object
            csv_key: CSV key for list locator
            expected_options: Expected options array
            csv_file: CSV filename constant
            timeout: Wait timeout in ms
        
        Returns:
            bool: True if validation passes
        
        Raises:
            AssertionError: If options don't match
        """
        locator = CommonMethods.get_values_from_csv(csv_key, csv_file)
        await page.wait_for_selector(locator, timeout=timeout)
        elements = page.locator(locator)
        count = await elements.count()
        
        assert count == len(expected_options), f"Option count mismatch: expected {len(expected_options)}, got {count}"
        
        for i in range(count):
            actual = (await elements.nth(i).text_content()).strip()
            expected = expected_options[i]
            assert actual == expected, f"Option {i} mismatch: expected '{expected}', got '{actual}'"
        
        Log.info(f"✓ Validated {count} options for {csv_key}")
        allure.after(f"✓ List options validated: {csv_key}")
        return True

    @staticmethod
    async def validate_fields(page: Page, fields: dict, csv_file: str, timeout: int = 5000) -> bool:
        """
        Validate multiple fields at once using a dictionary.
        
        Args:
            page: Playwright page object
            fields: Dict of {csv_key: expected_value}
            csv_file: CSV filename constant
            timeout: Wait timeout in ms
        
        Returns:
            bool: True if all validations pass
        
        Raises:
            AssertionError: If any field doesn't match
        """
        for csv_key, expected in fields.items():
            await CommonMethods.validate_text(page, csv_key, expected, csv_file, timeout)
        
        Log.info(f"✓ Validated {len(fields)} fields")
        return True

    @staticmethod
    async def validate_search_list(page: Page, csv_file: str, timeout: int = 5000) -> bool:
        """
        Validate search list options.
        
        Args:
            page: Playwright page object
            csv_file: CSV filename constant
            timeout: Wait timeout in ms
        
        Returns:
            bool: True if validation passes
            
        Note:
            Previously named 'validate_search_list_by_role' with role parameter.
            Removed role-based selection as search lists are now unified.
            Legacy role-based logic commented below for reference.
        """
        from utils.app_constants import AppConstants
        
        # Legacy role-based selection (kept for reference - not used in new UI)
        # if role.lower() == "auditor":
        #     expected_options = AppConstants.SEARCH_LIST_AUDITOR
        # elif role.lower() == "prospective":
        #     expected_options = AppConstants.SEARCH_LIST_PROSPECTIVE
        # else:
        #     expected_options = AppConstants.SEARCH_LIST
        
        # Use default search list
        expected_options = AppConstants.SEARCH_LIST
        
        return await CommonMethods.validate_list_options(page, "lst_SearchList", expected_options, csv_file, timeout)

    @staticmethod
    def normalize_date(date_str: str) -> str:
        """
        Normalize date string to a common format for comparison.
        Supports multiple date formats and converts them to MM/DD/YYYY format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            str: Normalized date in MM/DD/YYYY format
            
        Examples:
            "Jun 28, 1953" -> "6/28/1953"
            "6/28/1953" -> "6/28/1953"
            "1953-06-28" -> "6/28/1953"
        """
        from datetime import datetime
        
        # Common date formats
        date_formats = [
            "%b %d, %Y",      # Jun 28, 1953
            "%B %d, %Y",      # June 28, 1953
            "%m/%d/%Y",       # 6/28/1953
            "%Y-%m-%d",       # 1953-06-28
            "%d/%m/%Y",       # 28/06/1953
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime("%m/%d/%Y")
            except ValueError:
                continue
        
        # If no format matched, return original
        return date_str.strip()

