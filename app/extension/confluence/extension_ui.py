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

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.wait_for_page_loaded()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.click_login_button()
    #         if login_page.is_first_login():
    #             login_page.first_user_setup()
    #         all_updates_page = AllUpdates(webdriver)
    #         all_updates_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:open_page_with_macro")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/MYS/OSS")
            # provide id of the button element of the select drop-down macro
            '''
            e.g. 
            <button id="LIM-49141308-c856550e-f98c-437a-9803-f88ecca96396" style="min-width:max-content" 
            class="aui-button lim-dropdown aui-dropdown2-trigger" data-content-id="49141308" 
            data-macro-id="c856550e-f98c-437a-9803-f88ecca96396" 
            aria-controls="control-49141308-c856550e-f98c-437a-9803-f88ecca96396" data-save="true" data-email="false" 
            data-values="" data-variable-name="" data-multi-select="false" data-required="false" data-mtitle="" 
            data-vertical="false" resolved="" aria-haspopup="true" aria-expanded="false" aria-busy="false">
                    Select..
            </button>
            '''
            page.wait_until_visible((By.ID, "LIM-49141308-c856550e-f98c-437a-9803-f88ecca96396"))
        sub_measure()
    measure()
