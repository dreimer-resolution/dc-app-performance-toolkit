from selenium.webdriver.common.by import By
from util.api.confluence_clients import ConfluenceRestClient
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from util.conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.pages import Login, AllUpdates, AdminPage, PopupManager, Logout
from selenium.common.exceptions import TimeoutException
import time

def app_specific_logout(webdriver, datasets):

    @print_timing("selenium_app_specific_log_out")
    def measure():
        logout_page = Logout(webdriver)
        logout_page.go_to()
        pick_signed_in_user \
            = webdriver.find_elements("xpath", ".//div[@class='table-cell text-left content']")
        if len(pick_signed_in_user) > 0:
            pick_signed_in_user[0].click()
    measure()


def app_specific_action(webdriver, datasets):
    login_page = Login(webdriver)
    page = BasePage(webdriver)

    rest_client = ConfluenceRestClient(
        CONFLUENCE_SETTINGS.server_url,
        CONFLUENCE_SETTINGS.admin_login,
        CONFLUENCE_SETTINGS.admin_password,
        verify=CONFLUENCE_SETTINGS.secure,
    )

    @print_timing("selenium_app_specific_login")
    def measure():

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():

            username = datasets['current_session']['username']
            print(f"login_with_alb_auth, user: {username}")

            # open base url
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/")

            try:
                still_logged_in = webdriver.find_element("xpath", ".//*[@id='com-atlassian-confluence']")
                print(still_logged_in)
            except:

                try:
                    page.wait_until_visible((By.ID, "i0116"), timeout=30)
                except TimeoutException:
                    # User might still be signed in to Azure, try to log out and restart
                    print("Azure login page not found, attempting to log out from Azure and restart")
                    webdriver.get(
                        "https://login.microsoftonline.com/ede9c166-5c73-46ba-9efc-605bd207f1f6/oauth2/v2.0/logout")
                    time.sleep(2)

                    # Check if we need to pick a signed-in user to log out
                    pick_signed_in_user = webdriver.find_elements("xpath",
                                                                  ".//div[@class='table-cell text-left content']")
                    if len(pick_signed_in_user) > 0:
                        print(f"Found {len(pick_signed_in_user)} signed-in users, clicking first one to log out")
                        pick_signed_in_user[0].click()
                        time.sleep(2)

                    # Restart the test after logging out
                    print("Restarting test after Azure logout")
                    app_specific_action(webdriver, datasets)
                    return

                # wait for azure user input field to be shown
                page.wait_until_visible((By.ID, "i0116"))
                # get field object
                username_input = webdriver.find_element("xpath", ".//*[@id='i0116']")
                # clear existing value
                username_input.clear()
                # add username to it
                username_input.send_keys(username + "@azuread.lab.resolution.de")
                next_is_password = webdriver.find_element("xpath", ".//*[@id='idSIButton9']")
                next_is_password.click()

                try:
                    # if we don't see password input within 5 seconds ...
                    page.wait_until_visible((By.ID, "i0118"), 5)
                except TimeoutException:
                    # ... restart test
                    app_specific_action(webdriver, datasets)
                    return

                password_input = webdriver.find_element("xpath", ".//*[@id='i0118']")
                password_input.clear()

                # this is required to prevent StaleElementReferenceException
                actions = ActionChains(webdriver)
                actions.send_keys("justAnotherPassw0rd!")
                actions.send_keys(Keys.ENTER)
                actions.perform()

                yes_button = webdriver.find_element("xpath", ".//*[@id='idSIButton9']")
                yes_button.click()

                # wait for confluence page
                page.wait_until_visible((By.ID, "com-atlassian-confluence"))
                node_id = login_page.get_node_id()
                if node_id == '':
                    print(f"no node_id, restarting")
                    app_specific_action(webdriver, datasets)
                    return
                else:
                    print(f"logged in, got node_id: >{node_id}<")
                    node_ip = rest_client.get_node_ip(node_id)
                    webdriver.node_id = node_id
                    webdriver.node_ip = node_ip

                if login_page.is_first_login():
                    login_page.first_user_setup()
                all_updates_page = AllUpdates(webdriver)
                all_updates_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()