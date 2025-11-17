import re
from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='confluence')


@confluence_measure("locust_app_specific_action")
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action(locust):

    if 'user_deactivator' not in locust.cross_action_storage or locust.cross_action_storage['user_deactivator'] != 'true':
        body = {"notInGroups": ["confluence-users"], "action": "DEACTIVATE"}

        r = locust.post('/rest/de.resolution.userdeactivator/1.0/ui/users', json=body, catch_response=True)
        content = r.content.decode('utf-8')   # decode response content

        if 'resultId' not in content:
            logger.error(f"resultId was not found in {content}, looks like deactivation was not triggered properly")

        assert 'resultId' in content

        result_id_pattern = "resultId=(.+?)"
        result_id = re.findall(result_id_pattern, content)

        logger.locust_info(f"resultId: {result_id[0]}")
        assert int(result_id[0]) >= 0
        locust.cross_action_storage['user_deactivator'] = 'true'
