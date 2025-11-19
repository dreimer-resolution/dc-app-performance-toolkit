import requests
from locustio.common_utils import init_logger, bamboo_measure, run_as_specific_user  # noqa F401
from util.conf import BAMBOO_SETTINGS
logger = init_logger(app_type='bamboo')


@bamboo_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin') # doesn't work, the framework team needs to fix this
def app_specific_action(locust):
    username = "admin"
    password = "admin"
    connector_id = "008eee20-023d-40aa-a941-34be5084c927"
    # locust post ignores auth, so we need to use requests
    r = requests.post(f'{BAMBOO_SETTINGS.server_url}/rest/samlsso-admin/1.0/usersync/connector/{connector_id}/sync',
                  auth=(username, password))
    logger.info(f'Started User Sync Job')
    content = r.content.decode('utf-8')
    assertion_string = 'Scheduled with jobid'
    if assertion_string not in content:
        logger.error(f"assertion string '{assertion_string}' was not found in {content}")
    assert assertion_string in content
