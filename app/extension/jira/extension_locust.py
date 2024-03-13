import requests
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401
import random
logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):

    r = requests.get('https://jira.dc-testing.reslab.de/rest/api/2/issue/UM-1?fields=customfield_10106', auth=("admin", "admin"))
    json = r.json()
    current_story_points = json['fields']['customfield_10106']
    body = '{"fields": {"customfield_10106": ' + str(int(current_story_points + random.randint(10, 20))) + '}}'
    headers = {'content-type': 'application/json'}
    r = requests.put('https://jira.dc-testing.reslab.de/rest/api/2/issue/UM-1', body, headers=headers, auth=("admin", "admin"))
    assert r.status_code == 204


