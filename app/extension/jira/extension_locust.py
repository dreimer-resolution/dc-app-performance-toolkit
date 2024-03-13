import requests
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401
import random
import time
logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):
    get_start = time.time()
    r = requests.get('https://jira.dc-testing.reslab.de/rest/api/2/issue/UM-1?fields=customfield_10106', auth=("admin", "admin"))
    get_end = time.time()
    print("GET Issue: %s seconds" % str(get_end - get_start))

    json = r.json()
    current_story_points = json['fields']['customfield_10106']

    put_start = time.time()
    body = '{"fields": {"customfield_10106": ' + str(int(current_story_points + random.randint(10, 20))) + '}}'
    headers = {'content-type': 'application/json'}
    r = requests.put('https://jira.dc-testing.reslab.de/rest/api/2/issue/UM-1', body, headers=headers, auth=("admin", "admin"))
    put_end = time.time()
    print("PUT Issue: %s seconds" % str(put_end - put_start))

    assert r.status_code == 204


