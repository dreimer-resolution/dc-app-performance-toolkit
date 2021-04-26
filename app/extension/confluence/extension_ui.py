import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.confluence.pages.selectors import UrlManager, LoginPageLocators, AllUpdatesLocators, PopupLocators, \
    PageLocators, DashboardLocators, TopPanelLocators, EditorLocators

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:login_with_saml_sso")
        def sub_measure():

            print(f"login_with_saml_sso, user: {datasets['username']}")

            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()

            # trigger sso directly
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugins/servlet/samlsso?redirectTo=%2F")

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

            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()

        sub_measure()

    measure()
    PopupManager(webdriver).dismiss_default_popup()