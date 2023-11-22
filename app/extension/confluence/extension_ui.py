from selenium.webdriver.common.by import By
from selenium_ui.confluence import modules
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from util.conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Logout
from selenium.common.exceptions import TimeoutException


def app_specific_logout(webdriver, datasets):

    @print_timing("selenium_app_specific_log_out")
    def measure():
        logout_page = Logout(webdriver)
        # logout_page.go_to()
        # pick_signed_in_user \
        #     = webdriver.find_elements_by_xpath(".//div[@class='table-cell text-left content']")
        # if len(pick_signed_in_user) > 0:
        #     pick_signed_in_user[0].click()
        logout_page.go_to()
        pick_signed_in_user \
            = webdriver.find_elements("xpath",".//div[@class='table-cell text-left content']")
        if len(pick_signed_in_user) > 0:
            pick_signed_in_user[0].click()
    measure()


def app_specific_action(webdriver, datasets):
    login_page = Login(webdriver)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login")
    def measure():

        """
        @print_timing("selenium_app_specific_login:open_login_page")
        def sub_measure():
            login_page.go_to()
        sub_measure()
        """

        @print_timing("selenium_app_specific_login:login_and_view_dashboard")
        def sub_measure():

            print(f"login_with_alb_auth, user: {datasets['username']}")
            # try:
            #     # this is only present if we are logged in already
            #     webdriver.find_element_by_xpath(".//*[@id='com-atlassian-confluence']")
            # except: # if not, there is an excption and we need to login     # noqa E722

            # open base url
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/")

            try:
                still_logged_in = webdriver.find_element_by_xpath(".//*[@id='com-atlassian-confluence']")
                print(still_logged_in)
            except:
                # wait for azure user input field to be shown
                page.wait_until_visible((By.ID, "i0116"))
                # get field object
                username_input = webdriver.find_element_by_xpath(".//*[@id='i0116']")
                # clear existing value
                username_input.clear()
                # add username to it
                username_input.send_keys(datasets['username'] + "@azuread.lab.resolution.de")
                next_is_password = webdriver.find_element_by_xpath(".//*[@id='idSIButton9']")
                next_is_password.click()

                try:
                    # if we don't see password input within 5 seconds ...
                    page.wait_until_visible((By.ID, "i0118"), 5)
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

                yes_button = webdriver.find_element_by_xpath(".//*[@id='idSIButton9']")
                yes_button.click()

                # wait for confluence page
                page.wait_until_visible((By.ID, "com-atlassian-confluence"))
                webdriver.node_id = login_page.get_node_id()

                if login_page.is_first_login():
                    login_page.first_user_setup()
                all_updates_page = AllUpdates(webdriver)
                all_updates_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()