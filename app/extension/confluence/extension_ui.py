import dateutil.parser
import datetime
from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:verify_that_reminder_has_been_sent")
        def sub_measure():
            # open page by id in edit mode
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/display/MYS/OSS")

            # wait for page reminder icon/ link to be ready
            page.wait_until_visible((By.ID, "page-reminders-action"))

            # activate status window
            webdriver.find_element_by_xpath(".//*[@id='page-reminders-action']").click()

            # wait for list of reminders
            page.wait_until_visible((By.ID, "page-reminders-list-new"))

            # get last sent datetime from table cell (assuming there is just one reminder and ours is the first)
            last_sent_cell \
                = webdriver.find_element_by_xpath("/html/body/section[2]/div/div[2]/div/table/tbody/tr[2]/td[3]")
            last_sent_datetime = dateutil.parser.parse(last_sent_cell.text)

            # only if it's not older than 120 seconds the test succeeds
            assert last_sent_datetime > datetime.datetime.utcnow() - datetime.timedelta(seconds=120)

        sub_measure()
    measure()
