import random

from selenium.webdriver.common.by import By
from selenium_ui.bamboo import modules

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bamboo.pages.pages import Login
from util.conf import BAMBOO_SETTINGS


def app_specific_action(webdriver, datasets):
    modules.setup_run_data(datasets)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():

        @print_timing("selenium_app_specific_login:login_and_view_all_plans")
        def sub_measure():
            print(f"login_with_saml_sso, user: {datasets['username']}")
            # trigger sso directly
            page.go_to_url(f"{BAMBOO_SETTINGS.server_url}/plugins/servlet/samlsso")
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
            # wait for element on page
            page.wait_until_visible((By.ID, "page"))

        sub_measure()
    measure()
