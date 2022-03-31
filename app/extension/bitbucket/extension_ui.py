from selenium.webdriver.common.by import By
import time
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bitbucket.pages.pages import LoginPage, GetStarted
from util.conf import BITBUCKET_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = LoginPage(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.set_credentials(username=username, password=password)
            login_page.submit_login()
            get_started_page = GetStarted(webdriver)
            get_started_page.wait_for_page_loaded()
        app_specific_user_login(username='admin', password='admin')
    measure()

    """
    this test is intended to start a new sync, not to measure its duration
    """
    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:start_sync_and_wait_until_complete")
        def sub_measure():
            # open user sync page with one connector added already (set it up so that sync takes just a few seconds)
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/samlsso/usersync")
            # wait for sync button
            page.wait_until_visible((By.XPATH, ".//span[text()='Sync']"))

            # check if there is a sync still running, for that we'll fetch the whole reconfigure div text
            us_div = webdriver.find_element_by_xpath(".//*[@id='reconfigure-react-root']")

            # only try to start sync again if none is still running
            if "RUNNING" not in us_div.text:
                # click sync button
                webdriver.find_element_by_xpath(".//span[text()='Sync']").click()
                # wait for status window to open
                page.wait_until_visible((By.XPATH, ".//div[text()='Sync Status']"))
                # press close button
                webdriver.find_element_by_xpath(".//span[text()='Close']").click()
        sub_measure()
    measure()

