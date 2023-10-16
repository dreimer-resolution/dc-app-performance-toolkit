from selenium_ui.jira import modules
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing

from util.conf import JIRA_SETTINGS
from selenium_ui.jira.pages.pages import Login, PopupManager, Logout
from selenium.common.exceptions import TimeoutException


def app_specific_logout(webdriver, datasets):
    logout_page = Logout(webdriver)

    @print_timing("selenium_app_specific_log_out")
    def measure():
        logout_page.go_to()
        # pick_signed_in_user \
        #     = webdriver.find_element("xpath",".//div[@class='table-cell text-left content']")
        # if len(pick_signed_in_user) > 0:
        #     pick_signed_in_user[0].click()
        try:
            logout_user_table = webdriver.find_element("xpath",".//div[@class='table']")
            logout_user_table.click()
        except:
            print("no logout user table found")
        measure()


def app_specific_action(webdriver, datasets):
    modules.setup_run_data(datasets)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():
        login_page = Login(webdriver)

        @print_timing("selenium_app_specific_login:open_login_page")
        def sub_measure():
            login_page.go_to()
            # the code below wouldn't work with our app, we won't see the login page before authentication.
            # setting the webdriver node_id after login instead
            """
            webdriver.node_id = login_page.get_node_id()
            print(f"node_id:{webdriver.node_id}")
            """

        sub_measure()

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():
            print(f"login_with_alb_auth, user: {datasets['username']}")
            try:
                # todo: this is most likely obsolete now that we log out on Azure as well
                # this is only present if we are logged in already
                webdriver.find_element("xpath",".//*[@id='jira']")
            except:  # if not, there is an excption and we need to login     # noqa E722
                # open dashboard to trigger ALB auth
                page.go_to_url(f"{JIRA_SETTINGS.server_url}/secure/Dashboard.jspa")

                # wait for azure user input field to be shown
                page.wait_until_visible((By.ID, "i0116"))
                # get username field
                username_input = webdriver.find_element("xpath",".//*[@id='i0116']")
                # clear existing value
                username_input.clear()
                # add username to it
                username_input.send_keys(datasets['username'] + "@azuread.lab.resolution.de")
                next_is_password = webdriver.find_element("xpath",".//*[@id='idSIButton9']")
                next_is_password.click()

                try:
                    # if we don't see password input within 5 seconds ...
                    page.wait_until_visible((By.ID, "i0118"), 5)
                except TimeoutException:
                    # ... restart test
                    app_specific_action(webdriver, datasets)
                    return

                password_input = webdriver.find_element("xpath",".//*[@id='i0118']")
                password_input.clear()

                # this is required to prevent StaleElementReferenceException
                actions = ActionChains(webdriver)
                actions.send_keys("justAnotherPassw0rd!")
                actions.send_keys(Keys.ENTER)
                actions.perform()

                stay_signed_in_no = webdriver.find_element("xpath",".//*[@id='idBtn_Back']")
                stay_signed_in_no.click()

                # wait for html body id "jira" which is always present, both for users who never logged in and who did
                page.wait_until_visible((By.ID, "jira"))
                webdriver.node_id = login_page.get_node_id()
                print(f"node_id: {webdriver.node_id}")

                if login_page.is_first_login():
                    login_page.first_login_setup()
                if login_page.is_first_login_second_page():
                    login_page.first_login_second_page_setup()
                login_page.wait_for_page_loaded()

        sub_measure()

    measure()
    PopupManager(webdriver).dismiss_default_popup()
