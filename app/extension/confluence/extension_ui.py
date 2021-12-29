import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    # run action as admin user, impersonation doesn't work for the majority of users
    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_page_loaded()
            login_page.set_credentials(username=username, password=password)
            login_page.click_login_button()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        app_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:open_page_with_macro")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/MYS/OSS")
            # page.wait_until_visible((By.ID, "com-atlassian-confluence"))
            # page.wait_until_visible((By.ID, "main-content"))
            page.wait_until_visible((By.XPATH, "//iframe[starts-with(@class, 'ossa-macro conf-macro output-block')]"))
            page.wait_until_available_to_switch((By.XPATH,
                                                 "//iframe[starts-with(@class, 'ossa-macro conf-macro output-block')]"))
            page.wait_until_visible((By.XPATH,
                                     "//iframe[starts-with(@class, 'ossa-macro conf-macro output-block')]"
                                     and "//div[@class='ossa-table-wrapper']"))
        sub_measure()
    measure()
