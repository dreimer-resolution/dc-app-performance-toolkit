from util.conf import JIRA_SETTINGS
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium.common.exceptions import TimeoutException
from selenium_ui.jira.pages.pages import Login, PopupManager, Issue, Project, Search, ProjectsList, \
    BoardsList, Board, Dashboard, Logout

"""
Prerequisites: 
- changes performance users email address to ...@azuread.lab.resolution.de (Excel Connector)
- Grant admin consent to user permissions in app registration (this is done already for https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/CallAnAPI/appId/2beed0fd-1a83-42c9-8ebb-3be6d4192bd2/isMSAApp/) 
"""


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action:login_with_open_id_and_view_dashboard")
    def measure():

        login_page = Login(webdriver)
        login_page.delete_all_cookies()

        print(f"starting login_with_open_id, user: {datasets['username']}")

        page.go_to_url(f"{JIRA_SETTINGS.server_url}/secure/Dashboard.jspa")
        print(f"opened dashboard page for user: {datasets['username']}")
        # click on open-id login button
        page.wait_until_visible((By.ID, "openid-1"))
        webdriver.find_element_by_xpath(".//*[@id='openid-1']").click()
        print(f"clicked open id button for user: {datasets['username']}")

        # wait for azure user input field to be shown
        page.wait_until_visible((By.ID, "i0116"))
        # get username field
        username_input = webdriver.find_element_by_xpath(".//*[@id='i0116']")
        # clear existing value
        username_input.clear()
        # add username to it
        username_input.send_keys(datasets['username'] + "@azuread.lab.resolution.de")
        next_is_password = webdriver.find_element_by_xpath(".//*[@id='idSIButton9']")
        next_is_password.click()

        try:
            # if we don't see password input within 5 seconds ...
            page.wait_until_visible((By.ID, "i0118"), 1)
            print(f"no password prompt from azure - about to restart test for user: {datasets['username']}")
        except TimeoutException:
            # ... restart test
            app_specific_action(webdriver, datasets)
            return

        password_input = webdriver.find_element_by_xpath(".//*[@id='i0118']")
        password_input.clear()

        # this is required to prevent StaleElementReferenceException
        actions = ActionChains(webdriver)
        actions.send_keys("justAnotherPassw0rd!")
        actions.send_keys(Keys.ENTER)
        actions.perform()
        print(f"entered username and password in azure for user: {datasets['username']}")

        try:
            # if we don't see password input within 5 seconds ...
            page.wait_until_visible((By.ID, "idBtn_Back"), 1)
            stay_signed_in_no = webdriver.find_element_by_xpath(".//*[@id='idBtn_Back']")
            stay_signed_in_no.click()
        except TimeoutException:
            # ... restart test
            print(f"no stay signed in prompt from azure - about to restart test for user: {datasets['username']}")
            app_specific_action(webdriver, datasets)
            return

        """
        if page.get_elements(LoginPageLocators.continue_button):
            page.wait_until_visible(LoginPageLocators.continue_button).send_keys(Keys.ESCAPE)
            page.get_element(LoginPageLocators.continue_button).click()
            page.wait_until_visible(LoginPageLocators.avatar_page_next_button).click()
            page.wait_until_visible(LoginPageLocators.explore_current_projects).click()
            page.go_to_url(DashboardLocators.dashboard_url)
            page.wait_until_visible(DashboardLocators.dashboard_window)
        else:
            page.wait_until_visible((By.ID, "gadget-10002-title"))
        """

        print(f"before handling post login checks for user: {datasets['username']}")

        if login_page.is_first_login():
            login_page.first_login_setup()
        if login_page.is_first_login_second_page():
            login_page.first_login_second_page_setup()
        login_page.wait_for_page_loaded()
        webdriver.node_id = login_page.get_node_id()
        print(f"node_id: {webdriver.node_id}, username: {datasets['username']}")
    measure()
    PopupManager(webdriver).dismiss_default_popup()

