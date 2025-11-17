import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login, AdminPage
from util.conf import JIRA_SETTINGS


"""
This is just an example of how to use UD via selenium, could be used for SSO later.
This type of test is only applicable for actions which should be performed by every test user.
It's pointless to let 200 test users deactivate thousands of other users at the same time. 

Comment from Atlassian:

there are a bunch of ways to do that. As you mentioned:
 - Locust test with low concurrency
 - Run long running task manually during the test run (e.g. with REST)
 - Modify selenium test with a logic (if possible) - do not do long running task if it is in progress
    - Use dataset object in selenium test as a flag to start long running task in app-specific test one time. Something like:

def app_specific_action(webdriver, datasets):
    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:view_page")
        def sub_measure():
            if "app_specific_flag" not in datasets.keys():
                print("Do one time specific thing")
                datasets["app_specific_flag"] = True
        sub_measure()
    measure()

"""

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
    #         login_page.wait_for_login_page_loaded()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.wait_for_dashboard_or_first_login_loaded()
    #         if login_page.is_first_login():
    #             login_page.first_login_setup()
    #         if login_page.is_first_login_second_page():
    #             login_page.first_login_second_page_setup()
    #         login_page.wait_for_page_loaded()
    #         # uncomment below line to do web_sudo and authorise access to admin pages
    #         # AdminPage(webdriver).go_to(password=password)
    #
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:view_issue")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/userdeactivator/admin") # open bulk user page

            # Wait for filter button to appear, indicating users have been loaded
            page.wait_until_visible((By.XPATH, ".//span[text()='Filter']"))

            # Check first check box, selecting all users
            webdriver.find_element_by_xpath(".//input[@type='checkbox']")[0].click
            # press bulk operation button
            webdriver.find_element_by_xpath(".//button[span='Choose Bulk Action']")[0].click
            # select deactivation
            webdriver.find_element_by_xpath(".//input[@type='radio' and @value='1']")[0].click()
            # click next
            webdriver.find_element_by_xpath(".//button[span='Next']")[0].click()
            # confirm
            webdriver.find_element_by_xpath(".//button[span='Confirm']")[0].click()

            # Wait for operation to complete
            page.wait_until_visible((By.XPATH, ".//span[text()='Operation Done!']"))

            # close button
            webdriver.find_element_by_xpath(".//button[span='Close']")[0].click()


        sub_measure()
    measure()

