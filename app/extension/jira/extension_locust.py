import re
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
#@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action(locust):

    # this will trigger a usersync for connector with id 1
    r = locust.post('/rest/samlsso-admin/1.0/usersync/connector/1/sync', auth=("admin", "admin"), catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    if 'id' not in content:
        logger.error(f"id for sync was not found in {content}, looks like full sync was not triggered properly")

    assert 'id' in content

    result_id_pattern = '"id":(.+?)'
    result_id = re.findall(result_id_pattern, content)

    logger.locust_info(f"id: {result_id[0]}")
    assert int(result_id[0]) >= 0

    # RESET SESSION USER BACK, UNLESS WE DO THAT WE GET STRANGE
    # "ADMIN STILL LOGGED IN" ERRORS IN OTHER LOCUST ACTIONS
    # WE DO THAT WITH THIS DUMMY CALL:
    locust.get(f"/secure/BrowseProjects.jspa?selectedCategory=archived",
               catch_response=True, auth=(locust.session_data_storage["username"], "password"))
