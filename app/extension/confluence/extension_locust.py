import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')

"""

    login_body = {
        'os_username': '',
        'os_password': '',
        'os_cookie': True,
        'os_destination': '',
        'login': 'Log in'
    }
    TEXT_HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    login_body['os_username'] = 'admin'
    login_body['os_password'] = 'admin'
    locust.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    locust.post('/doauthenticate.action', auth=('admin', 'admin'), json={'authenticate':'Confirm', 'password': 'admin'}, catch_response=True )
    r = locust.post('/rest/de.resolution.userdeactivator/1.0/ui/users', json={"notInGroups":["confluence-users"],"action":"ACTIVATE"}, headers={'content-type': 'application/json', 'x-experimentalapi':'opt-in'}, catch_response=True)  # call app-specific GET endpoint
    login_body['os_username'] = locust.session_data_storage['username']
    login_body['os_password'] = 'password'
    locust.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.post('/rest/de.resolution.userdeactivator/1.0/ui/users', json={"notInGroups":["confluence-users"],"action":"ACTIVATE"}, headers={'content-type': 'application/json', 'x-experimentalapi':'opt-in'}, catch_response=True)  # call app-specific GET endpoint

"""



@confluence_measure("locust_app_specific_action")
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
