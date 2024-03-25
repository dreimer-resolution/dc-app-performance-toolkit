from selenium.webdriver.common.by import By
from selenium_ui.confluence import modules
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager


def app_specific_action(webdriver, datasets):
    modules.setup_run_data(datasets)
    login_page = Login(webdriver)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():
            username = datasets['current_session']['username']
            print(f"login_with_saml_sso, user: {username}")
            # trigger sso directly
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugins/servlet/samlsso?NameID=" + username)

            # wait for html body id which is always present, both for users who never logged in and who did
            page.wait_until_visible((By.ID, "com-atlassian-confluence"))

            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()
