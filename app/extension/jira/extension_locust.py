import re
from locustio.common_utils import init_logger, jira_measure

logger = init_logger(app_type='jira')


@jira_measure
def app_specific_action(locust):

    # this will trigger deactivation of everybody who is not in jira-software-users,
    # like our test users created with the test connector
    body = {"notInGroups": ["jira-software-users"], "action": "DEACTIVATE"}

    r = locust.post('/rest/de.resolution.userdeactivator/1.0/ui/users', auth=("admin", "admin"), json=body,  catch_response=True)
    content = r.content.decode('utf-8')

    if 'resultId' not in content:
        logger.error(f"resultId was not found in {content}, looks like deactivation was not triggered properly")

    assert 'resultId' in content

    result_id_pattern = '"resultId":(.+?)'
    result_id = re.findall(result_id_pattern, content)

    logger.locust_info(f"resultId: {result_id[0]}")
    assert int(result_id[0]) >= 0
