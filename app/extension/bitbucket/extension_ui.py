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

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:trigger_usersync")
        def sub_measure():
            # open user sync connector page
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/de.resolution.usersync/admin")
            # 1 sec pause to prevent 500 errors, obviously caused by trying to use the UI too quickly during automation
            time.sleep(1)
            # wait for table to be loaded
            page.wait_until_visible((By.ID, 'usersync-connector-table-body'))
            # check if there is a sync running already
            running_sync = webdriver.find_elements_by_xpath(".//span[.='Sync is running...']")
            # if not
            if len(running_sync) == 0:
                # another check to see if sync button is now available
                new_sync = webdriver.find_elements_by_xpath(".//span[.='Sync']")
                if len(new_sync) > 0:
                    # click on sync
                    webdriver.find_element_by_xpath(".//span[.='Sync']").click()
                    # wait for status window
                    page.wait_until_visible((By.ID, 'usersync-sync-status-dialog'))
                    # we are done here
        sub_measure()
    measure()
