"""
Central import file for the entire framework (tests, pages, utils).

Import this in your files to get all necessary dependencies:
    from utils.local_imports import *

This provides:
- pytest (with all decorators like @pytest.mark.asyncio, @pytest.mark.order)
- @step(n) - Shorthand decorator for ordered async tests
- Common Python modules (asyncio, re, typing)
- Playwright types (Page, TimeoutError)
- Framework utilities (Log, CommonMethods, OpenAIUtils, AppConstants)
- All fixtures are automatically available in tests (no need to import)
"""
import pytest
import asyncio
import re
from typing import List, Dict, Optional, Any, Tuple
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

# Framework utilities
from utils.logger import Log
from utils.common_methods import CommonMethods, AllureHelper as allure
from utils.openai_utils import OpenAIUtils
from utils.app_constants import AppConstants


def step(order):
    """
    Shorthand decorator for ordered async tests.
    Combines @pytest.mark.order(n) and @pytest.mark.asyncio into one line.
    
    Usage:
        @step(1)
        async def test_step1_login(self, login_page, config):
            ...
    
    Args:
        order: The execution order number for the test
    """
    def decorator(func):
        func = pytest.mark.order(order)(func)
        func = pytest.mark.asyncio(func)
        return func
    return decorator


# Re-export everything
__all__ = [
    'pytest', 'step', 'asyncio', 're',
    'List', 'Dict', 'Optional', 'Any', 'Tuple',
    'Page', 'PlaywrightTimeoutError',
    'Log', 'CommonMethods', 'allure',
    'OpenAIUtils', 'AppConstants'
]

