import re
from locustio.common_utils import init_logger, confluence_measure
import time

logger = init_logger(app_type='confluence')


@confluence_measure
def app_specific_action(locust):

    # create token with description for current perf user
    current_user = locust.session_data_storage["username"]

    logger.locust_info(f'current_user: {current_user} ')

    token_description =  "token_" + str(int(round(time.time() * 1000)))
    body =  {"tokenDescription": token_description} # create token payload
    r = locust.post('/rest/de.resolution.apitokenauth/latest/user/token', json=body, catch_response=True)
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
    r = locust.get('/rest/api/user/current', auth=(current_user, plain_text_token[0]), catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    username_pattern = '"username":"(.+?)"'
    username_for_assertion = re.findall(username_pattern, content)

    logger.locust_info(f'username from /rest/api/user/current response: {username_for_assertion[0]}')

    if username_for_assertion[0] != current_user:
        logger.error(f" username in response not found/ not matching the current username")

    assert username_for_assertion[0] == current_user
