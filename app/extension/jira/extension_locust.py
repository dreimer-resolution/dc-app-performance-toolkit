import re
from locustio.common_utils import init_logger, jira_measure

logger = init_logger(app_type='jira')


@jira_measure
def app_specific_action(locust):

    # add header key and value for http header auth to log us in
    current_user = locust.session_data_storage["username"]

    # execute a GET request
    r = locust.get('/rest/api/2/myself', headers={"X-AUTH": current_user}, catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    # expecting the same username in the response
    username_pattern = '"name":"(.+?)"'
    username_for_assertion = re.findall(username_pattern, content)

    logger.locust_info(f'username from /rest/api/2/myself response: {username_for_assertion[0]}')

    if username_for_assertion[0] != current_user:
        logger.error(f" username in response not found/ not matching the current username")

    assert username_for_assertion[0] == current_user
