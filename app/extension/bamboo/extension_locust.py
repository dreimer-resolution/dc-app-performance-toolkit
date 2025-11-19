import re
from locustio.common_utils import init_logger, bamboo_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='bamboo')


@bamboo_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')
def app_specific_action(locust):
    username = "admin"
    password = "admin"
    headers = {'content-type': 'application/json'}
    r = locust.post('/rest/samlsso-admin/1.0/usersync/connector/008eee20-023d-40aa-a941-34be5084c927/sync',
                    headers, auth=(username, password), catch_response=True)
    logger.info(f'Started User Sync Job')
    content = r.content.decode('utf-8')
    assertion_string = 'Scheduled with jobid'
    if assertion_string not in content:
        logger.error(f"assertion string '{assertion_string}' was not found in {content}")
    assert assertion_string in content
