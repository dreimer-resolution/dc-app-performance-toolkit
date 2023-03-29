from selenium_ui.jira import modules
from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing

from util.conf import JIRA_SETTINGS
from selenium_ui.jira.pages.pages import Login, PopupManager


def app_specific_action(webdriver, datasets):
    modules.setup_run_data(datasets)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():
        # login_page = Login(webdriver)
        #
        # @print_timing("selenium_app_specific_login:open_login_page")
        # def sub_measure():
        #     login_page.go_to()
        #     webdriver.node_id = login_page.get_node_id()
        #     print(f"node_id:{webdriver.node_id}")
        # sub_measure()

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():
            print(f"login_with_saml_sso, user: {datasets['username']}")
            # trigger sso directly
            # page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso?redirectTo=%2Fsecure%2FDashboard.jspa")
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/samlsso?NameID=" + datasets['username'])

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

            # wait for html body id "jira" which is always present, both for users who never logged in and who did
            page.wait_until_visible((By.ID, "jira"))

            if login_page.is_first_login():
                login_page.first_login_setup()
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()
            webdriver.node_id = login_page.get_node_id()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()
