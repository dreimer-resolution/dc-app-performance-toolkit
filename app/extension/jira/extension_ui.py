import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:view_issue")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/<>")

            # wait for external share tab/ iframe to be ready
            # for now by id. might change. classname is "external-share-iframe"
            page.wait_until_visible((By.ID, "jes-frame-AbIS8RX2YA"))
            page.wait_until_available_to_switch((By.ID, "jes-frame-AbIS8RX2YA"))

            # < button class ="button primary" > Create External Share Link < / button >

            """
            <a target="_blank" 
            href="https://jobo-jira-sd.klab.resolution.de/plugins/servlet/share/issue/69a7fe13-9968-4ee5-8206-565824226957">
            [SD1-1] External Share Link</a>
            """

            # page.return_to_parent_frame()

        sub_measure()
    measure()

