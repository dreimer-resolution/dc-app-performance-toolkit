import re
from locustio.common_utils import init_logger, confluence_measure
import time

logger = init_logger(app_type='confluence')

"""
This test requires a space called ISS with a page called Crew Section
"""


@confluence_measure
def app_specific_action(locust):

    random_short_url =  str(int(round(time.time() * 1000)))

    r = locust.get('/', catch_response=True)
    base_url = r.url

    # create a short URL
    null = None
    body = {
        "id": null,
        "shortUrl": random_short_url,
        "longUrl": base_url + "/display/ISS/Crew+Section",
        "note": "Meet the Crew",
        "anchor": null
    }
    r = locust.post('/rest/vanityurl-admin/2.0/urlmappings', json=body, catch_response=True)
    content = r.content.decode('utf-8')

    if 'creationDate' not in content:
        logger.error(f"creationDate was not found in {content}, looks like the short URL was not created")

    assert 'creationDate' in content  # assert if plain text token is contained in response

    short_url_pattern = '"shortUrl":"(.+?)"'
    short_url_from_result = re.findall(short_url_pattern, content)

    creation_date_from_result_pattern = '"creationDate":"(.+?)"'
    creation_date_from_result = re.findall(creation_date_from_result_pattern, content)

    logger.locust_info(f"created shortUrl: {short_url_from_result[0]}, creationDate is {creation_date_from_result[0]}")


    # request short URL
    r = locust.get('/go/' + short_url_pattern, catch_response=True)

    if r.status_code != 200:
        logger.error(f"calling the shortUrl {short_url_from_result[0]} didn't return status 200")

    assert r.status_code == 200
