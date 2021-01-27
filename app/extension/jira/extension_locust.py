import re
from locustio.common_utils import init_logger, jira_measure

logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
def app_specific_action(locust):


    # this will trigger deactivation of everybody who is not in jira-software-users,
    # like our test users created with the test connector
    body = {"notInGroups": ["jira-software-users"], "action": "DEACTIVATE"}

    r = locust.post('/rest/de.resolution.userdeactivator/1.0/ui/users', auth=("admin", "admin"), json=body,  catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    if 'resultId' not in content:
        logger.error(f"resultId was not found in {content}, looks like deactivation was not triggered properly")

    assert 'resultId' in content

    result_id_pattern = '"resultId":(.+?)'
    result_id = re.findall(result_id_pattern, content)

    logger.locust_info(f"resultId: {result_id[0]}")
    assert int(result_id[0]) >= 0


    # RESET SESSION USER BACK, UNLESS WE DO THAT WE GET STRANGE
    # "ADMIN STILL LOGGED IN" ERRORS IN OTHER LOCUST ACTIONS
    # WE DO THAT WITH THIS DUMMY CALL:
    locust.get(f"/secure/BrowseProjects.jspa?selectedCategory=archived",
               catch_response=True, auth=(locust.session_data_storage["username"], "password"))
