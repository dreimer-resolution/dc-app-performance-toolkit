import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS
from selenium_ui.jira.pages.pages import Login, PopupManager, Issue, Project, Search, ProjectsList, \
    BoardsList, Board, Dashboard, Logout

from selenium_ui.jira.pages.selectors import UrlManager, LoginPageLocators, DashboardLocators, PopupLocators, \
    IssueLocators, ProjectLocators, SearchLocators, BoardsListLocators, BoardLocators, LogoutLocators

"""
https://social.technet.microsoft.com/wiki/contents/articles/24541.powershell-bulk-create-ad-users-from-csv-file.aspx
https://www.alitajran.com/create-active-directory-users-from-csv-with-powershell/
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
        @print_timing("selenium_app_custom_action:login_with_saml_sso")
        def sub_measure():
            print(f"login_with_saml_sso, user: {datasets['username']}")

            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso") # open dashboard page with login screen


            # trigger sso directly
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso")

            # wait for nameID input field to be shown
            page.wait_until_visible((By.ID, "nameID"))

            # get field object
            username_input = webdriver.find_element_by_xpath(".//*[@id='nameID']")

            # clear existing value
            username_input.clear()

            # add username to it
            username_input.send_keys(datasets['username'])

            # click send button
            webdriver.find_element_by_xpath(".//*[@class='btn btn-default']").click()

            if page.get_elements(LoginPageLocators.continue_button):
                page.wait_until_visible(LoginPageLocators.continue_button).send_keys(Keys.ESCAPE)
                page.get_element(LoginPageLocators.continue_button).click()
                page.wait_until_visible(LoginPageLocators.avatar_page_next_button).click()
                page.wait_until_visible(LoginPageLocators.explore_current_projects).click()
                page.go_to_url(DashboardLocators.dashboard_url)
                page.wait_until_visible(DashboardLocators.dashboard_window)
            else:
                page.wait_until_visible((By.ID, "gadget-10002-title"))

        sub_measure()

        PopupManager(webdriver).dismiss_default_popup()

    measure()

