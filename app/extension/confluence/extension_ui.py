import time

from selenium.webdriver.common.by import By
from util.api.confluence_clients import ConfluenceRestClient
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from util.conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.pages import Login, AllUpdates, AdminPage, PopupManager, Logout
from selenium.common.exceptions import TimeoutException, WebDriverException

AZURE_TENANT_ID = "ede9c166-5c73-46ba-9efc-605bd207f1f6"
AZURE_LOGOUT_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/logout"
AZURE_EMAIL_DOMAIN = "azuread.lab.resolution.de"
AZURE_PASSWORD = "justAnotherPassw0rd!"

# A failing login is retried a few times and then reported as a failed action.
# It must never be retried indefinitely: bzt's pytest_runner only checks its
# -d/--duration deadline after pytest.main() returns, so a login that never
# returns hangs the whole run and no results.csv/results_summary.log is written.
LOGIN_ATTEMPTS = 3

# Shown on the Azure sign-out page when Azure still knows a signed-in account.
AZURE_ACCOUNT_ROW = (By.XPATH, ".//div[@class='table-cell text-left content']")
# Present once Confluence itself has rendered.
CONFLUENCE_LOADED = (By.ID, "com-atlassian-confluence")


def _reset_sessions(webdriver, page):
    """Drop the Confluence, ALB and Azure sessions so the next request forces a fresh sign-in.

    delete_all_cookies() only clears cookies of the page that is currently loaded,
    so both hosts have to be visited: the Confluence session and the ALB's
    AWSELBAuthSessionCookie live on the Confluence host, the Azure session and the
    cached account tiles that produce the "Pick an account" page live on
    login.microsoftonline.com. Clearing Confluence/ALB first means that even if the
    ALB cookie has already expired (which redirects us to Azure) the Azure step
    below still cleans up.
    """
    page.go_to_url(CONFLUENCE_SETTINGS.server_url)
    webdriver.delete_all_cookies()

    webdriver.get(AZURE_LOGOUT_URL)
    time.sleep(2)
    accounts = webdriver.find_elements(*AZURE_ACCOUNT_ROW)
    if accounts:
        print(f"Azure logout: {len(accounts)} signed-in account(s) listed, picking the first")
        accounts[0].click()
        time.sleep(2)
    webdriver.delete_all_cookies()


def _open_azure_email_form(webdriver, timeout=30):
    """Wait for the Azure e-mail field, clicking through the account picker if shown.

    Azure answers the ALB's authorize request with either the e-mail form (#i0116)
    or the "Pick an account" tile page (#tilesHolder), where "Use another account"
    (#otherTile) leads on to the e-mail form.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if webdriver.find_elements(By.ID, "i0116"):
            return
        other_account = webdriver.find_elements(By.ID, "otherTile")
        if other_account:
            print("Azure account picker shown, choosing 'Use another account'")
            try:
                other_account[0].click()
            except WebDriverException:
                pass  # tile went stale while Azure re-rendered, the next pass re-checks
        time.sleep(0.5)

    if webdriver.find_elements(*CONFLUENCE_LOADED):
        raise AssertionError(
            "Reached Confluence without an Azure prompt - the ALB/Azure session was not "
            "cleared, so the logged in user cannot be guaranteed")
    raise TimeoutException(
        f"Azure e-mail form (#i0116) did not appear within {timeout}s. "
        f"Current URL: {webdriver.current_url[:200]}")


def _submit_azure_credentials(webdriver, page, username):
    email_input = webdriver.find_element(By.ID, "i0116")
    email_input.clear()
    email_input.send_keys(f"{username}@{AZURE_EMAIL_DOMAIN}")
    webdriver.find_element(By.ID, "idSIButton9").click()

    page.wait_until_visible((By.ID, "i0118"), timeout=10)
    webdriver.find_element(By.ID, "i0118").clear()

    # ActionChains instead of send_keys to prevent StaleElementReferenceException
    actions = ActionChains(webdriver)
    actions.send_keys(AZURE_PASSWORD)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    # "Stay signed in?" does not always appear
    try:
        page.wait_until_visible((By.ID, "idBtn_Back"), timeout=5)
        webdriver.find_element(By.ID, "idBtn_Back").click()
    except TimeoutException:
        print("Stay signed in prompt not shown, continuing...")


def _enter_confluence(webdriver, page, login_page, rest_client):
    page.wait_until_visible(CONFLUENCE_LOADED)

    # get_node_id() returns None when the footer carries no node info, so test for
    # falsiness rather than == '' - otherwise None reaches the REST lookup below.
    node_id = login_page.get_node_id()
    if not node_id:
        raise AssertionError("Confluence page footer carried no node id")
    print(f"logged in, got node_id: >{node_id}<")
    webdriver.node_id = node_id
    try:
        webdriver.node_ip = rest_client.get_node_ip(node_id)
    except Exception as error:
        # keep this retryable rather than failing the login outright
        raise AssertionError(f"Could not look up IP of node {node_id}: {error}") from error

    if login_page.is_first_login():
        login_page.first_user_setup()
    AllUpdates(webdriver).wait_for_page_loaded()


def _verify_logged_in_user(webdriver, expected_username):
    """Confirm the Confluence session really belongs to the user of this iteration."""
    actual = webdriver.execute_script(
        "var m = document.querySelector('meta[name=\"ajs-remote-user\"]');"
        "return m ? m.content : null;")
    if actual is None:
        print(f"WARNING: no ajs-remote-user meta tag, could not verify login of {expected_username}")
        return
    if actual != expected_username:
        raise AssertionError(
            f"Logged in as '{actual}' but this session expects '{expected_username}'")
    print(f"verified logged in user: {actual}")


def app_specific_logout(webdriver, datasets):

    @print_timing("selenium_app_specific_log_out")
    def measure():
        # /logout.action starts IdP single-logout and redirects to Azure's
        # "Which account do you want to sign out of?" page, so the account row is
        # what has to be clicked.
        logout_page = Logout(webdriver)
        logout_page.go_to()
        accounts = webdriver.find_elements(*AZURE_ACCOUNT_ROW)
        if accounts:
            accounts[0].click()
        else:
            print("Azure sign-out account row not shown, session may already be gone")

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

            # Always sign in from scratch. Reusing a still valid ALB/Confluence
            # session would run the iteration as whatever user logged in last, not
            # as the user this session was handed.
            last_error = None
            for attempt in range(1, LOGIN_ATTEMPTS + 1):
                try:
                    _reset_sessions(webdriver, page)
                    # triggers the ALB auth redirect to Azure
                    page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/")
                    _open_azure_email_form(webdriver)
                    _submit_azure_credentials(webdriver, page, username)
                    _enter_confluence(webdriver, page, login_page, rest_client)
                    _verify_logged_in_user(webdriver, username)
                    return
                except (WebDriverException, AssertionError) as error:
                    last_error = error
                    detail = (str(error).splitlines() or [''])[0][:200]
                    print(f"Azure login attempt {attempt}/{LOGIN_ATTEMPTS} failed for "
                          f"{username}: {type(error).__name__}: {detail}")

            raise Exception(
                f"Azure login failed for {username} after {LOGIN_ATTEMPTS} attempts"
            ) from last_error

        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()
