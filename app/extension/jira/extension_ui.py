import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing

from util.conf import JIRA_SETTINGS
from selenium_ui.jira.pages.pages import Login, PopupManager, Issue, Project, Search, ProjectsList, \
    BoardsList, Board, Dashboard, Logout

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
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso?redirectTo=%2Fsecure%2FDashboard.jspa")

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
                login_page.first_login_setup()
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()

        sub_measure()
    measure()

    PopupManager(webdriver).dismiss_default_popup()

