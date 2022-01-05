import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         if login_page.is_first_login():
    #             login_page.first_login_setup()
    #         if login_page.is_first_login_second_page():
    #             login_page.first_login_second_page_setup()
    #         login_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:view_issue_and_wait_for_s3_file_to_be_shown")
        def sub_measure():
            # open an issue where the s3 list is included
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/AANES-152")
            # wait 4 link to text file called org.hotovo.confluence.amazon-s3-storage-connector.txt in s3 connector list
            page.wait_until_visible(
                (By.XPATH, "//*[@title='[AmazonS3 Files] org.hotovo.confluence.amazon-s3-storage-connector.txt']"))
        sub_measure()
    measure()

