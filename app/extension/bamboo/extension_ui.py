import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bamboo.pages.pages import Login
from util.conf import BAMBOO_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.set_credentials(username=username, password=password)
            login_page.click_login_button()
        app_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:start_sync_and_wait_until_complete")
        def sub_measure():
            # open user sync page with one connector added already (set it up so that sync takes just a few seconds)
            page.go_to_url(f"{BAMBOO_SETTINGS.server_url}/plugins/servlet/samlsso/usersync")
            # wait for sync button
            page.wait_until_visible((By.XPATH, ".//span[text()='Sync']"))
            # click sync button
            webdriver.find_element_by_xpath(".//span[text()='Sync']").click()
            # wait for span with content DONE, indicating sync has been completed
            page.wait_until_visible((By.XPATH, ".//span[text()='DONE']"))
            # press close button
            webdriver.find_element_by_xpath(".//span[text()='Close']").click()
        sub_measure()
    measure()
