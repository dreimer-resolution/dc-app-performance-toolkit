
import re
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):

    # create token with description for current perf user
    current_user = locust.session_data_storage["username"]
    token_description =  "token_" + str(int(round(time.time() * 1000)))
    body = '{"tokenDescription": "' + token_description + '"}'  # create token payload
    headers = {'content-type': 'application/json'}

    r = locust.post('/rest/de.resolution.apitokenauth/latest/user/token', body, headers, catch_response=True)
    content = r.content.decode('utf-8')

    if 'plainTextToken' not in content:
        logger.error(f"a plainTextToken was not found in {content}")

    assert 'plainTextToken' in content  # assert if plain text token is contained in response

    plain_text_token_pattern = '"plainTextToken":"(.+?)"'
    plain_text_token = re.findall(plain_text_token_pattern, content)
    token_description_from_result_pattern = '"tokenDescription":"(.+?)"'
    token_description_from_result = re.findall(token_description_from_result_pattern, content)

    logger.locust_info(f'plainTextToken: {plain_text_token[0]} with description {token_description_from_result[0]} for user {current_user}')

    # use that token for another GET request
    r = locust.get('/rest/api/2/myself', auth=(current_user, plain_text_token[0]), catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    username_pattern = '"name":"(.+?)"'
    username_for_assertion = re.findall(username_pattern, content)

    logger.locust_info(f'username from /rest/api/2/myself response: {username_for_assertion[0]}')

    if username_for_assertion[0] != current_user:
        logger.error(f" username in response not found/ not matching the current username")

    assert username_for_assertion[0] == current_user


