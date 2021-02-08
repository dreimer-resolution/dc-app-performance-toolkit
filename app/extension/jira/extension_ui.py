import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS
from selenium_ui.jira.pages.pages import PopupManager


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
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/secure/Dashboard.jspa") # open dashboard page with login screen

            page.wait_until_visible((By.ID, "openid-1"))

            webdriver.find_element_by_xpath(".//*[@id='openid-1']").click()

            page.wait_until_visible((By.ID, "userNameInput"))
            page.wait_until_visible((By.ID, "passwordInput"))

            username_input = webdriver.find_element_by_xpath(".//*[@id='userNameInput']")
            username_input.send_keys("ad\\" + datasets['username'][0:20])

            password_input = webdriver.find_element_by_xpath(".//*[@id='passwordInput']")
            password_input.send_keys('just4lab!')

            webdriver.find_element_by_xpath(".//*[@id='submitButton']").click()
            PopupManager(webdriver).dismiss_default_popup()


        sub_measure()
    measure()
