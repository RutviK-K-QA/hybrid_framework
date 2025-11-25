"""OpenAI utilities for self-healing locators."""
import re
import asyncio
from typing import Optional
from openai import OpenAI
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.logger import Log
from utils.common_methods import CommonMethods
from utils.app_constants import AppConstants


class OpenAIUtils:
    """OpenAI utility class for locator self-healing."""

    def __init__(self):
        """Initialize OpenAI utils."""
        Log.info("OpenAIUtils constructor")

    @staticmethod
    def generate_response(prompt: str, api_key: str) -> Optional[str]:
        """
        Generate response from OpenAI.
        
        Args:
            prompt: The prompt to send
            api_key: OpenAI API key
            
        Returns:
            str: Generated response or None
        """
        try:
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response.choices and len(response.choices) > 0:
                result = response.choices[0].message.content.strip()
                Log.info(f"Response: {result}")
                return result
            else:
                Log.info("No response generated.")
                return "No response generated."
        except Exception as e:
            Log.error(f"An error occurred: {e}")
            return None

    @staticmethod
    def generate_response_new(prompt: str) -> Optional[str]:
        """
        Generate response from OpenAI with retries.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            str: Generated response or None
        """
        try:
            client = OpenAI(api_key=AppConstants.API_KEY, timeout=60.0)
            
            request_data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            return OpenAIUtils._call_openai_with_retries(client, request_data, max_retries=3)
        except Exception as e:
            Log.error(f"Error in generate_response_new: {e}")
            return None

    @staticmethod
    def _call_openai_with_retries(client: OpenAI, request_data: dict, max_retries: int = 3) -> Optional[str]:
        """
        Call OpenAI API with retries.
        
        Args:
            client: OpenAI client
            request_data: Request data
            max_retries: Maximum number of retries
            
        Returns:
            str: Generated response or None
        """
        for i in range(max_retries):
            try:
                response = client.chat.completions.create(**request_data)
                
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content.strip()
                else:
                    return "No response generated."
            except Exception as e:
                Log.error(f"Attempt {i + 1} failed: {e}")
                if i == max_retries - 1:
                    raise RuntimeError(f"Max retries reached. Unable to get a response.") from e
                
                # Wait before retrying
                import time
                time.sleep(2)
        
        return "No response generated after retries."

    async def verify_and_get_locators_using_ai(
        self, 
        page: Page, 
        element: str, 
        file_name: str
    ) -> Optional[str]:
        """
        Verify locator and get corrected version using AI if needed.
        
        Args:
            page: Playwright page instance
            element: Element name
            file_name: CSV file name
            
        Returns:
            str: Valid locator or None
        """
        try:
            locator = CommonMethods.get_values_from_csv(element, file_name)
            
            if not locator:
                Log.error(f"Locator not found for element: {element}")
                return None
            
            try:
                # Wait for selector with timeout
                await page.wait_for_selector(locator, timeout=10000)
                
                if await page.is_visible(locator):
                    return locator
            except (PlaywrightTimeoutError, Exception) as e:
                Log.warn(f"Locator {locator} not found, trying AI correction...")
                
                # Get DOM content
                dom_content = await page.content()
                
                # Create prompt for AI
                prompt = (
                    f"As a seasoned QA Analyst, your mission is to analyze the DOM (Document Object Model) "
                    f"of a web application and recommend the most appropriate locator for {locator} "
                    f"to identify and interact with specific elements. Your goal is to provide a robust "
                    f"and reliable set of locator that will ensure the stability and maintainability "
                    f"of your test automation framework. : {dom_content} "
                    f"And Do not provide any extra description and By.Locatorname as well, "
                    f"just return result as locator = <correct_locator>"
                )
                
                try:
                    corrected_locator = OpenAIUtils.generate_response_new(prompt)
                    
                    if corrected_locator:
                        corrected_locator = self._extract_xpath_from_response(corrected_locator)
                        Log.info(f"Corrected XPath suggested by AI: {corrected_locator}")
                        
                        # Import allure if available for reporting
                        try:
                            import allure
                            allure.attach(
                                f"Corrected XPath suggested by AI: {corrected_locator}",
                                name="AI Correction",
                                attachment_type=allure.attachment_type.TEXT
                            )
                        except ImportError:
                            pass
                        
                        CommonMethods.update_locator(element, corrected_locator, file_name)
                        return corrected_locator
                except Exception as ai_exception:
                    Log.error(f"AI troubleshooting failed: {ai_exception}")
        except Exception as e:
            Log.error(f"Error in verify_and_get_locators_using_ai: {e}")
        
        return None

    def _extract_xpath_from_response(self, response: str) -> Optional[str]:
        """
        Extract XPath from AI response.
        
        Args:
            response: AI response string
            
        Returns:
            str: Extracted XPath or None
        """
        # Regular expression to match patterns in quotes
        pattern = re.compile(r'"(.*?)"')
        matcher = pattern.search(response)
        
        if matcher:
            return matcher.group(1)
        
        return None

