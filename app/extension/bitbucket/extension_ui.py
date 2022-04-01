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

            # important, retrieves the atlassian app version
            login_page = LoginPage(webdriver)
            login_page.go_to()
            webdriver.app_version = login_page.get_app_version()
            login_page.delete_all_cookies()

            # trigger sso directly
            # page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/samlsso?redirectTo=%2Fgetting-started")
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/samlsso?NameID=" + datasets['username'])

            """
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
            """

            # using end-of-test code from atlassian again (deals with first time login/ validates successful login)
            get_started_page = GetStarted(webdriver)
            get_started_page.wait_for_page_loaded()

        sub_measure()
    measure()
