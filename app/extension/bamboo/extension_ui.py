from selenium.webdriver.common.by import By
from selenium_ui.bamboo import modules
from selenium.webdriver.common.action_chains import ActionChains
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bamboo.pages.pages import Logout
from util.conf import BAMBOO_SETTINGS
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


def app_specific_logout(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_log_out")
    def measure():
        page.go_to_url(f"{BAMBOO_SETTINGS.server_url}/userLogout.action")
        pick_signed_in_user \
            = webdriver.find_elements_by_xpath(".//div[@class='table-cell text-left content']")
        pick_signed_in_user[0].click()
    measure()


def app_specific_action(webdriver, datasets):
    modules.setup_run_data(datasets)
    page = BasePage(webdriver)

    @print_timing("selenium_app_specific_login:login_and_view_all_plans")
    def measure():
        """
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f"{current_time} - starting sso for user: {datasets['username']}")
        # trigger sso directly
        page.go_to_url(f"{BAMBOO_SETTINGS.server_url}/plugins/servlet/samlsso")
        # wait for nameID input field to be shown
        page.wait_until_visible((By.ID, "nameID"))
        current_time = time.strftime("%H:%M:%S", t)
        print(f"{current_time} - name id field is available")
        # get field object
        username_input = webdriver.find_element_by_xpath(".//*[@id='nameID']")
        # clear existing value
        username_input.clear()
        # add username to it
        username_input.send_keys(datasets['username'])
        # click send button
        webdriver.find_element_by_xpath(".//*[@class='btn btn-default']").click()
        current_time = time.strftime("%H:%M:%S", t)
        print(f"{current_time} - clicked send button")
        # wait for element on page
        page.wait_until_visible((By.ID, "page"))
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f"{current_time} - successfully logged in user: {datasets['username']}")
        """

        # open url to trigger SSO
        page.go_to_url(f"{BAMBOO_SETTINGS.server_url}/plugins/servlet/samlsso")

        # wait for azure user input field to be shown
        page.wait_until_visible((By.ID, "i0116"))
        # get username field
        username_input = webdriver.find_element_by_xpath(".//*[@id='i0116']")
        # clear existing value
        username_input.clear()
        # add username to it
        username_input.send_keys(datasets['username'] + "@azuread.lab.resolution.de")
        # username_input.send_keys("performance_user_aotvp@azuread.lab.resolution.de")
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

        stay_signed_in_no = webdriver.find_element_by_xpath(".//*[@id='idBtn_Back']")
        stay_signed_in_no.click()

        """
        page.wait_until_visible((By.ID, "userNameInput"))
        page.wait_until_visible((By.ID, "passwordInput"))

        username_input = webdriver.find_element_by_xpath(".//*[@id='userNameInput']")
        username_input.send_keys("ad\\" + datasets['username'][0:20])

        password_input = webdriver.find_element_by_xpath(".//*[@id='passwordInput']")
        password_input.send_keys('just4lab!')

        webdriver.find_element_by_xpath(".//*[@id='submitButton']").click()
        """
        # wait for build plan dashboard table
        page.wait_until_visible((By.ID, "dashboard"))

    measure()
