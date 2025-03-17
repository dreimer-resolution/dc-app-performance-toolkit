import requests
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401
import json
import random
import time
logger = init_logger(app_type='jira')


@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):

    headers = {'content-type': 'application/json'}
    """
    # customfield_10105 = sprint reference
    create_issue_payload = {
        "fields": {
            "project":
                {
                    "key": "UM"
                },
            "summary": "Sprint issue test #" + str(time.time()),
            "description": "REST APIs are great.",
            "issuetype": {
                "name": "Bug"
            },
            "customfield_10105": 5
        }
    }

    create_start = time.time()
    r = requests.post('https://jira.dcapt.reslab.de/rest/api/2/issue', json.dumps(create_issue_payload),
                      headers=headers, auth=("admin", "admin"))
    create_end = time.time()
    logger.locust_info(f'*********** POST Issue: {str(create_end - create_start)} seconds')
    resp_json = r.json()
    issue_key = resp_json['key']
    """

    issue_key = "UM-" + str(int(random.randint(1, 300)))
    story_points = str(int(random.randint(5, 30)))

    put_story_points_start = time.time()
    body = '{"fields": {"customfield_10106": ' + story_points + '}}'
    r = requests.put('https://jira.dcapt.reslab.de/rest/api/2/issue/' + issue_key, body, headers=headers, auth=("admin", "admin"))
    put_story_points_end = time.time()
    logger.locust_info(f'*********** PUT Issue: {str(put_story_points_end - put_story_points_start)} seconds')
    assert r.status_code == 204

    """
    # delete issue again to not blow up the sprint
    delete_start = time.time()
    r = requests.delete('https://jira.dcapt.reslab.de/rest/api/2/issue/' + issue_key, headers=headers, auth=("admin", "admin"))
    delete_end = time.time()
    logger.locust_info(f'*********** DEL Issue ({str(r.status_code)}): {str(delete_end - delete_start)} seconds')
    """



