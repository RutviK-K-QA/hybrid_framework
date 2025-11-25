# RAAPID Automation Framework

A modern Python async Playwright automation framework with AI-powered self-healing capabilities, built for reliable web application testing.

## 🚀 Features

- **Async Playwright** - Fast, reliable browser automation
- **Page Object Model** - Clean, maintainable test architecture
- **AI Self-Healing** - Automatic locator correction using OpenAI
- **CSV Locator Repository** - Centralized element management
- **Allure Reporting** - Beautiful, detailed test reports
- **Multi-browser Support** - Chrome, Chromium, Firefox, WebKit
- **Easy Configuration** - Properties-based setup

## 📁 Project Structure

```
├── pages/              # Page Object Model classes
├── utils/              # Utilities (factory, logger, OpenAI, constants)
├── tests/              # Test files (conftest.py - do not modify)
├── configs/            # Configuration files
│   ├── config.properties      # Active configuration
│   └── test_data/             # Historical test data
├── object_repository/  # Element locators (CSV files)
├── reports/            # Test execution reports
├── logs/               # Log files
├── requirements.txt    # Python dependencies
└── pytest.ini         # Pytest configuration
```

## ⚡ Quick Start

### 1. Setup (First Time)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Install Playwright browsers

### 2. Configure

Edit `configs/config.properties`:
```properties
url = https://your-app-url.com
username = your_username
password = your_password
Project = Your_Project_Name
```

### 3. Run Tests

Activate the virtual environment first:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

Then run tests:
```bash
# Run example test
pytest tests/test_example.py -v

# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_smoke_ra_audit.py -v

# Run with specific browser
pytest tests/ --browser=chrome
pytest tests/ --browser=firefox
```

### 4. View Results

- **Logs**: `logs/test_execution.log`
- **HTML Report**: `reports/report.html`
- **Screenshots**: `reports/*.png` (on failure)

## 📝 Writing New Tests

### Basic Test Structure

Create a new file in `tests/` directory (e.g., `test_my_feature.py`):

```python
"""My feature tests."""
from utils.local_imports import *

class TestMyFeature:
    """Class-based tests - all page objects auto-injected via self."""
    
    @step(1)
    async def test_login(self):
        """Test login functionality."""
        result = await self.login_page.login_with_mfa(
            self.config["username"],
            self.config["password"],
            self.config
        )
        assert result is True
    
    @step(2)
    async def test_change_project(self):
        """Test project change."""
        result = await self.landing_page.change_project("automation_c2")
        assert result is True
```

### Key Points for Writing Tests:

1. **Use class-based tests** - All page objects automatically available via `self`
2. **Use `@step(n)` decorator** - Combines `@pytest.mark.asyncio` and `@pytest.mark.order(n)`
3. **Access pages via self** - `self.login_page`, `self.home_page`, `self.landing_page`, etc.
4. **Access config via self** - `self.config["key"]`
5. **No fixture parameters needed** - All injected automatically into the test class
6. **Use `async def`** - Test functions must be async with `await` for page methods

## 🎯 Test Fixtures Explained

Fixtures automatically provide everything your tests need without manual imports.

### What Are Fixtures?

Fixtures are pre-configured objects injected into your tests. They're defined in `tests/conftest.py`.

### Available Page Objects (Auto-Injected)

All page objects and config are automatically available in class-based tests via `self`:

| Access via self | What It Provides | Example Usage |
|-------------|------------------|-------------|
| `self.page` | Playwright Page object | Direct browser control |
| `self.config` | Configuration dictionary | `self.config["username"]` |
| `self.login_page` | LoginPage instance | `await self.login_page.login_with_mfa(...)` |
| `self.landing_page` | LandingPage instance | `await self.landing_page.change_project(...)` |
| `self.home_page` | HomePage instance | `await self.home_page.verify_audit_product_texts()` |
| `self.working_screen_page` | WorkingScreenPage instance | Working screen tests |
| `self.working_screen_page_audit` | Audit page instance | Audit workflow tests |
| `self.common_methods` | CommonMethods instance | Utility methods |

### How to Use in Tests

**All pages are automatically available via `self` in class-based tests:**

```python
from utils.local_imports import *

class TestLogin:
    @step(1)
    async def test_login(self):
        """Test login - no parameters needed!"""
        # All page objects auto-injected via self
        result = await self.login_page.login_with_mfa(
            self.config["username"],
            self.config["password"],
            self.config
        )
        assert result is True
```

**No fixture parameters needed!** Everything is auto-injected into `self`.

### Why Use Fixtures?

✅ **No manual object creation**
```python
# ❌ Old way - manual setup
page = await browser.new_page()
login_page = LoginPage(page)

# ✅ New way - automatic via fixture
async def test_something(login_page: LoginPage):
    # Already ready to use!
```

✅ **Automatic cleanup** - Fixtures handle browser close, session management

✅ **Session reuse** - Within a test class, browser stays open for speed

✅ **Cleaner test code** - Focus on test logic, not setup

### Test Class Structure for Session Reuse

```python
from utils.local_imports import *

class TestMyWorkflow:
    """Tests in this class share one browser session."""
    
    @step(1)
    async def test_step1_login(self):
        """Step 1: Login."""
        result = await self.login_page.login_with_mfa(
            self.config["username"], 
            self.config["password"], 
            self.config
        )
        assert result is True
    
    @step(2)
    async def test_step2_navigate(self):
        """Step 2: Navigate (browser still open from step 1)."""
        result = await self.landing_page.change_project("MyProject")
        assert result is True
```

**Key Point:** All tests in `TestMyWorkflow` class run in same browser session. Browser closes after all tests complete.

### Fixture Scopes

Defined in `conftest.py`:

- **`scope="class"`** - One instance per test class (browser, page)
- **`scope="function"`** - New instance per test (page objects)

This means:
- Browser opens once per test class
- Page objects are fresh for each test
- Login session persists across tests in a class

## 🎯 Creating New Page Objects

### Step 1: Create the Page Class

Create a new file in `pages/` directory:

```python
"""My new page object."""
from playwright.async_api import Page
from utils.logger import Log
from utils.common_methods import CommonMethods
from utils.openai_utils import OpenAIUtils
from utils.app_constants import AppConstants


class MyNewPage:
    """My new page class."""

    def __init__(self, page: Page):
        """Initialize page."""
        Log.info("MyNewPage constructor")
        self.page = page
        self.openai_utils = OpenAIUtils()

    async def my_action(self, param: str) -> bool:
        """
        Perform my action.
        
        Args:
            param: Some parameter
            
        Returns:
            bool: True if successful
        """
        try:
            # Get locator from CSV
            locator = await self.openai_utils.verify_and_get_locators_using_ai(
                self.page, "element_name", AppConstants.MY_ELEMENTS_CSV
            )
            
            # Perform action
            await self.page.click(locator)
            
            Log.info("Action completed successfully")
            return True
        except Exception as e:
            Log.error(f"Error: {e}")
            return False
```

### Step 2: Add Fixture to conftest.py

Edit `tests/conftest.py` and add:

```python
from pages.my_new_page import MyNewPage

@pytest.fixture(scope="function")
async def my_new_page(page) -> MyNewPage:
    """Get MyNewPage instance."""
    return MyNewPage(page)
```

### Step 3: Add CSV Locators

Create `object_repository/MyPage_Elements.csv`:
```csv
Element Name,Locator
my_button,"//button[@id='submit']"
my_input,"input[name='username']"
```

### Step 4: Use in Tests

```python
@pytest.mark.asyncio
async def test_my_feature(my_new_page: MyNewPage):
    """Test using my new page."""
    result = await my_new_page.my_action("test_param")
    assert result is True
```

## 🔍 Validation Helpers

The framework provides one-liner validation methods for common testing patterns.

### Available Validation Methods

All methods are in `CommonMethods` class:

#### 1. Text Validation
Validate a single element's text matches expected value:

```python
await CommonMethods.validate_text(
    page,                                    # Playwright page
    "lbl_Title",                            # Element name from CSV
    AppConstants.EXPECTED_TITLE,            # Expected text
    AppConstants.LOGIN_ELEMENTS             # CSV file
)
```

**What it does:**
1. Looks up "lbl_Title" in Login_Elements.csv
2. Gets the locator (e.g., "//h1[@class='title']")
3. Finds element on page and extracts text
4. Compares with expected value
5. Passes ✅ if match, fails ❌ with clear error

#### 2. Popup Validation
Validate popup/dialog title AND message together:

```python
await CommonMethods.validate_popup(
    page,
    AppConstants.WARNING_TITLE,             # Expected title
    AppConstants.WARNING_MESSAGE,           # Expected message
    AppConstants.WORKING_ELEMENTS
)
```

#### 3. List/Dropdown Options Validation
Validate dropdown options match expected array:

```python
await CommonMethods.validate_list_options(
    page,
    "chk_RejectOptions",                    # Dropdown element
    AppConstants.REJECT_OPTIONS,            # Expected array
    AppConstants.WORKING_ELEMENTS
)
```

#### 4. Multiple Fields at Once
Validate several fields using a dictionary:

```python
await CommonMethods.validate_fields(page, {
    "lbl_Model": AppConstants.HCC_MODEL,
    "lbl_Version": AppConstants.HCC_MODEL_VERSION,
    "lbl_DOB": AppConstants.HCC_DOB
}, AppConstants.WORKING_ELEMENTS)
```

#### 5. Search List Validation
Validate search list options:

```python
await CommonMethods.validate_search_list(
    page,
    AppConstants.LANDING_ELEMENTS
)
```

### When to Use Validation Helpers

**Use for:**
- ✅ Verifying page titles, labels, messages
- ✅ Checking popup/dialog content
- ✅ Validating dropdown options
- ✅ Confirming default values
- ✅ Testing role-based content

**Don't use for:**
- ❌ Simple visibility checks (use `page.is_visible()`)
- ❌ Navigation verification (use URL checks)
- ❌ Element presence only (use `wait_for_selector()`)

### Example: Adding Validation to Page Object

```python
class MyPage:
    async def verify_success_message(self) -> bool:
        """Verify success message appears."""
        try:
            # One-liner validation
            await CommonMethods.validate_text(
                self.page,
                "lbl_SuccessMsg",
                AppConstants.SUCCESS_MESSAGE,
                AppConstants.MY_ELEMENTS
            )
            return True
        except AssertionError as e:
            Log.error(f"Validation failed: {e}")
            return False
```

## 🔧 Configuration

### config.properties

Main configuration file with test data and URLs:
```properties
url = https://your-app.com
username = user
password = pass
Project = ProjectName
NPINo = 1234567890
```

### pytest.ini

Pytest configuration for markers and options:
```ini
[pytest]
markers =
    order: test execution order
    smoke: smoke tests
    audit: audit tests
```

### CSV Locator Files

Element locators stored in `object_repository/`:
- `Login_Elements.csv`
- `LandingPage_Elements.csv`
- `HomePage_Elements.csv`
- `WorkingPage_Elements.csv`

Format:
```csv
Element Name,Locator
btnLogin,"//button[@id='login']"
txtUsername,"input[name='username']"
```

## 🤖 AI Self-Healing

The framework automatically corrects broken locators using OpenAI:

1. When a locator fails, the framework captures the page DOM
2. Sends it to OpenAI for analysis
3. Receives a corrected locator
4. Updates the CSV file automatically
5. Continues test execution

**To enable**: Set your OpenAI API key in `utils/app_constants.py`:
```python
API_KEY = "your-openai-api-key"
```

## 📊 Test Reporting

### HTML Report
```bash
pytest tests/ --html=reports/report.html --self-contained-html
```
Open `reports/report.html` in browser.

### Allure Report
```bash
# Generate results
pytest tests/ --alluredir=reports/allure-results

# View report
allure serve reports/allure-results
```

## 🎨 Test Markers

Use markers to organize and run specific test groups:

```python
@pytest.mark.smoke
@pytest.mark.audit
@pytest.mark.order(1)
async def test_something():
    pass
```

Run tests by marker:
```bash
pytest tests/ -m smoke
pytest tests/ -m audit
```

## 🐛 Debugging

### View Logs
```bash
tail -f logs/test_execution.log  # Linux/Mac
Get-Content logs\test_execution.log -Wait  # Windows PowerShell
```

### Run Single Test with Debug
```bash
pytest tests/test_example.py::test_simple_login_example -v -s
```

### Common Issues

**Import Errors:**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

**Browser Not Found:**
```bash
playwright install
```

**Locator Not Found:**
- Check CSV file in `object_repository/`
- Enable AI self-healing with valid OpenAI API key
- Check element name matches CSV exactly

## 📦 Dependencies

Main packages (see `requirements.txt` for full list):
- `playwright` - Browser automation
- `pytest` - Testing framework
- `allure-pytest` - Test reporting
- `openai` - AI self-healing
- `jproperties` - Configuration management

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          playwright install chromium
      - run: pytest tests/ --browser=chromium
```

## 🎓 Best Practices

1. **Keep tests independent** - Each test should work standalone
2. **Use Page Objects** - Don't put locators directly in tests
3. **Add logging** - Use `Log.info()` for important steps
4. **Handle waits** - Use `await page.wait_for_selector()`
5. **Clean up** - Tests should clean up after themselves
6. **Use fixtures** - Reuse common setup via fixtures
7. **Order tests** - Use `@pytest.mark.order()` for sequential flows

## 📞 Need Help?

- Check logs in `logs/` directory
- Review test reports in `reports/` directory
- See `QUICK_START.md` for common commands

## 📄 License

Proprietary - RAAPID Inc.

---

**Version:** 1.0.0  
**Python:** 3.8+  
**Playwright:** 1.40.0
