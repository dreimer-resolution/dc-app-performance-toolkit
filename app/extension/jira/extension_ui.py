from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login, AdminPage
from util.conf import JIRA_SETTINGS
import time


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_issues']:
        issue_key = datasets['custom_issue_key']

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_login_page_loaded()
            login_page.set_credentials(username=username, password=password)
            login_page.wait_for_dashboard_or_first_login_loaded()
            if login_page.is_first_login():
                login_page.first_login_setup()
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()
            # uncomment below line to do web_sudo and authorise access to admin pages
            AdminPage(webdriver).go_to(password=password)

        app_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:start_sync_and_wait_until_complete")
        def sub_measure():
            # open user sync page with one connector added already (set it up so that sync takes just a few seconds)
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso/usersync")
            # wait for sync button
            page.wait_until_visible((By.XPATH, ".//span[text()='Sync']"))

            # check if there is a sync still running, for that we'll fetch the whole reconfigure div text
            us_div = webdriver.find_element("xpath", ".//*[@id='reconfigure-react-root']")

            # only try to start sync again if none is still running
            if "RUNNING" not in us_div.text:
                # click sync button
                webdriver.find_element("xpath", ".//span[text()='Sync']").click()
                # wait for status window to open
                page.wait_until_visible((By.XPATH, ".//div[text()='Sync Status']"))
                # press close button
                webdriver.find_element("xpath", ".//span[text()='Close']").click()
        sub_measure()
    measure()


