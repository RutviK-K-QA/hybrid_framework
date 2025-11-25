"""Login page object."""
from utils.local_imports import *

class LoginPage:
    """Login page class."""

    def __init__(self, page: Page):
        """Initialize LoginPage."""
        Log.info("Login page constructor")
        self.page = page
        self.openai_utils = OpenAIUtils()

    async def is_forgot_pwd_link_exist(self) -> bool:
        """
        Check if forgot password link exists.
        
        Returns:
            bool: True if link exists
        """
        lnk_forgot_password = CommonMethods.get_values_from_csv(
            "lnkForgotPassword", 
            AppConstants.LOGIN_ELEMENTS
        )
        return await self.page.is_visible(lnk_forgot_password)

    async def is_login_using_azure_ad_link_exist(self) -> bool:
        """
        Check if Azure AD login link exists.
        
        Returns:
            bool: True if link exists
        """
        lnk_azure_ad = CommonMethods.get_values_from_csv(
            "lnkAzureAd", 
            AppConstants.LOGIN_ELEMENTS
        )
        return await self.page.is_visible(lnk_azure_ad)

    async def login_with_mfa(self, username: str, password: str, config: dict = None) -> bool:
        """
        Login to the application.
        
        Args:
            username: Username
            password: Password
            config: Configuration dictionary (optional, required for MFA)
            
        Returns:
            bool: True if login successful
        """
        try:
            # Attach test info to Allure report
            allure.before("Verify user should be able to Login Successfully")
            
            # Get username field locator
            str_un_locator = CommonMethods.get_values_from_csv(
                "txtUsername", AppConstants.LOGIN_ELEMENTS
            )         
            await asyncio.sleep(3)    
            # reload page
            await self.page.reload()
            # Fill credentials
            Log.info(f"Filling username: {username}")
            await self.page.fill(str_un_locator, username)
            # Get password field locator
            str_pwd_locator = CommonMethods.get_values_from_csv(
                "txtPassword", AppConstants.LOGIN_ELEMENTS
            )
            Log.info(f"Filling password")
            await self.page.fill(str_pwd_locator, password)
            
            # Get login button locator
            btn_login = CommonMethods.get_values_from_csv(
                "btnLogin", AppConstants.LOGIN_ELEMENTS
            )
            await self.page.click(btn_login)
            Log.info("Login button clicked")
            
            # Handle MFA if page appears
            try:
                # Get MFA input locator
                mfa_input_locator = CommonMethods.get_values_from_csv(
                    "txtMfaCode", AppConstants.LOGIN_ELEMENTS
                )
                await self.page.wait_for_selector(mfa_input_locator, timeout=5000)
                
                Log.info("MFA page detected, generating TOTP code")
                
                # Determine MFA secret key based on username
                mfa_secret_key = "mfa_secret"
                if "automation" in username.lower():
                    mfa_secret_key = "mfa_secret_automation"
                elif "review" in username.lower():
                    mfa_secret_key = "mfa_secret_reviewL2" if "l2" in username.lower() else "mfa_secret_review"
                
                if not config:
                    Log.error("Config not provided for MFA authentication")
                    return False
                
                mfa_secret = config.get(mfa_secret_key)
                if not mfa_secret:
                    Log.error(f"MFA secret not found for {username} (key: {mfa_secret_key})")
                    return False
                
                # Generate and enter TOTP code using CommonMethods
                totp_code = CommonMethods.generate_totp_code(mfa_secret)
                await self.page.fill(mfa_input_locator, totp_code)
                Log.info("TOTP code entered")
                
                # Submit MFA
                mfa_submit_btn = CommonMethods.get_values_from_csv(
                    "btnMfaSubmit", AppConstants.LOGIN_ELEMENTS
                )
                await self.page.click(mfa_submit_btn)
                Log.info("MFA submitted")
            except Exception as e:
                Log.info(f"MFA not required or error: {e}")
                pass
            
            # Wait for navigation away from login page
            await self.page.wait_for_timeout(6000)  # Give time for navigation
            
            # Check if login was successful by verifying URL changed from main login
            current_url = self.page.url
            Log.info(f"Current URL after login: {current_url}")

            home_url = config.get("home_url")            
            if current_url == home_url:
                Log.info("Logged in Successfully - navigated to home page from login page")
                
                allure.after(f"Logged in Successfully - Current URL: {current_url}")
                return True
            else:
                Log.error("Login unsuccessful - still on main login page")
                return False
        except Exception as e:
            Log.error(f"Error during login: {e}")
            return False

    async def logout(self) -> bool:
        """
        Logout from the application.
        
        Returns:
            bool: True if logout successful
        """
        try:
            # Attach test info to Allure report
            allure.before("Verify user should be Logout from the application")
            
            # Check for "Later" button and click if visible
            btn_later = CommonMethods.get_values_from_csv(
                "btn_Later", 
                AppConstants.WORKING_ELEMENTS
            )
            if await self.page.is_visible(btn_later):
                await self.page.click(btn_later)
                ico_profile = CommonMethods.get_values_from_csv(
                    "ico_Profile", AppConstants.LANDING_ELEMENTS
                )
                await self.page.wait_for_selector(ico_profile)
            
            # Click profile icon
            ico_profile = CommonMethods.get_values_from_csv(
                "ico_Profile", AppConstants.LANDING_ELEMENTS
            )
            await self.page.wait_for_selector(ico_profile)
            await self.page.click(ico_profile)
            
            # Click logout link
            lnk_logout = CommonMethods.get_values_from_csv(
                "lnk_Logout", AppConstants.LANDING_ELEMENTS
            )
            await self.page.wait_for_selector(lnk_logout)
            await self.page.click(lnk_logout)
            
            # Verify username field is visible (back to login page)
            txt_username = CommonMethods.get_values_from_csv(
                "txtUsername", AppConstants.LOGIN_ELEMENTS
            )
            await self.page.wait_for_selector(txt_username)
            
            return await self.page.is_visible(txt_username)
        except Exception as e:
            Log.error(f"Error during logout: {e}")
            return False

