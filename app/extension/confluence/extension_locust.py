import re
import requests
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')


@confluence_measure("locust_app_specific_action")
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
#@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action(locust):

    # add header key and value for http header auth to log us in
    current_user = locust.session_data_storage["username"]

    # execute a GET request, but using python requests because we have a locust session we can't clear
    r = requests.get('https://confluence.dcapt.reslab.de/rest/api/user/current',
                     headers={"X-AUTH": current_user})
    content = r.content.decode('utf-8')   # decode response content

    # expecting the same username in the response
    username_pattern = '"username":"(.+?)"'
    username_for_assertion = re.findall(username_pattern, content)

    logger.locust_info(f'username from /rest/api/user/current response: {username_for_assertion[0]}')

    if username_for_assertion[0] != current_user:
        logger.error(f" username in response not found/ not matching the current username")

    assert username_for_assertion[0] == current_user
