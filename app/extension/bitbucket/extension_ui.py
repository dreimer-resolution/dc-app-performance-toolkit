import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bitbucket.pages.pages import LoginPage, GetStarted
from util.conf import BITBUCKET_SETTINGS

"""
- SSO redirection needs to be disabled, so that regular framework tests using the default login don't fail
- IdP selection needs to be set to use lowest weight IdP
- IdP is our test-Idp, so that we don't need to care for passwords and users

"""


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:login_with_saml_sso")
        def sub_measure():
            print(f"login_with_saml_sso, user: {datasets['username']}")

            # trigger sso directly
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/samlsso")

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

            # # wait for insecure warning proceed button (TODO)
            # page.wait_until_visible((By.ID, "proceed-button"))
            #
            # # click it
            # webdriver.find_element_by_xpath(".//*[@id='proceed-button']").click()


            # wait for repositories picker to be shown
            page.wait_until_visible((By.ID, "repositories-menu-trigger"))

            # get_started_page = GetStarted(webdriver)
            # get_started_page.wait_for_page_loaded()

        sub_measure()


    measure()


    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_logout action

    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = LoginPage(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.submit_login()
    #         get_started_page = GetStarted(webdriver)
    #         get_started_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    # @print_timing("selenium_app_custom_action")
    # def measure():
    #
    #     @print_timing("selenium_app_custom_action:view_repo_page")
    #     def sub_measure():
    #         page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/projects/{project_key}/repos/{repo_slug}/browse")
    #         page.wait_until_visible((By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')) # Wait for repo navigation panel is visible
    #         page.wait_until_visible((By.ID, 'ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT'))  # Wait for you app-specific UI element by ID selector
    #     sub_measure()
    # measure()
