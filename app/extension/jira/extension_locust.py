import requests
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401
import random
import time
logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
def app_specific_action(locust):

    headers = {'content-type': 'application/json'}
    issue_key = "UM-" + str(int(random.randint(1, 300)))
    story_points = str(int(random.randint(5, 30)))

    put_story_points_start = time.time()
    body = '{"fields": {"customfield_10106": ' + story_points + '}}'
    r = requests.put('https://jira.dcapt.reslab.de/rest/api/2/issue/' + issue_key, body, headers=headers, auth=("admin", "admin"))
    put_story_points_end = time.time()
    logger.locust_info(f'*********** PUT Issue: {str(put_story_points_end - put_story_points_start)} seconds')
    assert r.status_code == 204




