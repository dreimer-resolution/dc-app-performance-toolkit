from selenium.webdriver.common.by import By
from selenium_ui.confluence import modules
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager
from util.api.confluence_clients import ConfluenceRestClient

def app_specific_action(webdriver, datasets):
    rest_client = ConfluenceRestClient(
        CONFLUENCE_SETTINGS.server_url,
        CONFLUENCE_SETTINGS.admin_login,
        CONFLUENCE_SETTINGS.admin_password,
        verify=CONFLUENCE_SETTINGS.secure,
    )
    modules.setup_run_data(datasets)
    login_page = Login(webdriver)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():

        @print_timing("selenium_app_specific_login:get_node_id_and_node_ip")
        def sub_measure():
            login_page.go_to()
            if login_page.is_logged_in():
                login_page.delete_all_cookies()
                login_page.go_to()
            login_page.wait_for_page_loaded()
            node_id = login_page.get_node_id()
            node_ip = rest_client.get_node_ip(node_id)
            webdriver.node_ip = node_ip

        sub_measure()

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

            # node_info_span = webdriver.find_element("xpath", ".//*[@id='footer-cluster-node']")
            # node_id = node_info_span.text.split(':')[-1].replace(')', '').replace(' ', '')
            # node_ip = rest_client.get_node_ip(node_id)
            # webdriver.node_ip = node_ip

        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()
