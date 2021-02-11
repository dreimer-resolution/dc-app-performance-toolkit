import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.confluence.pages.selectors import UrlManager, LoginPageLocators, AllUpdatesLocators, PopupLocators, \
    PageLocators, DashboardLocators, TopPanelLocators, EditorLocators

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout


"""
https://social.technet.microsoft.com/wiki/contents/articles/24541.powershell-bulk-create-ad-users-from-csv-file.aspx
https://www.alitajran.com/create-active-directory-users-from-csv-with-powershell/
"""

def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)


    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:login_with_open_id")
        def sub_measure():
            print(f"login_with_open_id, user: {datasets['username'][0:20]}")
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/login.action") # open dashboard page with login screen

            page.wait_until_visible((By.ID, "openid-1"))

            webdriver.find_element_by_xpath(".//*[@id='openid-1']").click()

            page.wait_until_visible((By.ID, "userNameInput"))
            page.wait_until_visible((By.ID, "passwordInput"))

            username_input = webdriver.find_element_by_xpath(".//*[@id='userNameInput']")
            username_input.send_keys("ad\\" + datasets['username'][0:20])

            password_input = webdriver.find_element_by_xpath(".//*[@id='passwordInput']")
            password_input.send_keys('just4lab!')

            webdriver.find_element_by_xpath(".//*[@id='submitButton']").click()

            if page.get_elements(LoginPageLocators.first_login_setup_page):
                if page.get_element(LoginPageLocators.current_step_sel).text == 'Welcome':
                    page.wait_until_clickable(LoginPageLocators.skip_welcome_button).click()
                if page.get_element(LoginPageLocators.current_step_sel).text == 'Upload your photo':
                    page.wait_until_clickable(LoginPageLocators.skip_photo_upload).click()
                if page.get_element(LoginPageLocators.current_step_sel).text == 'Find content':
                    page.wait_until_any_element_visible(LoginPageLocators.skip_find_content)[0].click()
                    page.wait_until_clickable(LoginPageLocators.finish_setup).click()

            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()

        sub_measure()
    measure()
