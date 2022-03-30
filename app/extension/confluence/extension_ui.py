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

        # @print_timing("selenium_app_specific_login:open_login_page")
        # def sub_measure():
        #     login_page.go_to()
        #     if login_page.is_logged_in():
        #         login_page.delete_all_cookies()
        #         login_page.go_to()
        #     login_page.wait_for_page_loaded()
        #     webdriver.node_id = login_page.get_node_id()
        #     print(f"node_id:{webdriver.node_id}")
        # sub_measure()

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():
            print(f"login_with_saml_sso, user: {datasets['username']}")
            # trigger sso directly
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugins/servlet/samlsso?redirectTo=%2F")

            """
            # Test IdP
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
            
            page.wait_until_visible((By.ID, "userNameInput"))
            page.wait_until_visible((By.ID, "passwordInput"))

            username_input = webdriver.find_element_by_xpath(".//*[@id='userNameInput']")
            username_input.send_keys("ad\\" + datasets['username'][0:20])

            password_input = webdriver.find_element_by_xpath(".//*[@id='passwordInput']")
            password_input.send_keys('just4lab!')

            webdriver.find_element_by_xpath(".//*[@id='submitButton']").click()



            # wait for html body id which is always present, both for users who never logged in and who did
            page.wait_until_visible((By.ID, "com-atlassian-confluence"))

            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()
