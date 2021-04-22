import time
from selenium import webdriver


# datasets = {
#     'username': 'performance_odcaiyswid',
#     'password': 'just4lab!'
# }

datasets = {
    'username': 'other',
    'password': 'just4lab!'
}

datasets = {
    'username': 'dcapt-perf-user-qmyuy',
    'password': 'just4lab!'
}

sleep_time = 1


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--unsafely-treat-insecure-origin-as-secure=http://bitbucket-loadbala-1v3fdiqusich2-1005687555.us-east-1.elb.amazonaws.com')

webdriver = webdriver.Chrome(options=chrome_options)  # Optional argument, if not specified will search path.


# webdriver.get('http://jira-loadb-t0v24a9y7u9s-1750178515.us-east-1.elb.amazonaws.com/secure/Dashboard.jspa');
# webdriver.get('https://jobo-bb.klab.resolution.de/plugins/servlet/samlsso');
webdriver.get('http://bitbucket-loadbala-1v3fdiqusich2-1005687555.us-east-1.elb.amazonaws.com/plugins/servlet/samlsso')

time.sleep(sleep_time) 

#webdriver.find_element_by_xpath(".//*[@id='openid-1']").click()
#time.sleep(sleep_time)

username_input = webdriver.find_element_by_xpath(".//*[@id='nameID']")
username_input.clear()
username_input.send_keys(datasets['username'])

# time.sleep(sleep_time)
#
# password_input = webdriver.find_element_by_xpath(".//*[@id='passwordInput']")
# password_input.send_keys(datasets['password'])

time.sleep(sleep_time)

webdriver.find_element_by_xpath(".//*[@class='btn btn-default']").click()

time.sleep(sleep_time)
#
webdriver.find_element_by_xpath(".//*[@id='proceed-button']").click()

user_span = webdriver.find_element_by_xpath(".//*[@id='current-user']")
user_span.click()



# search_box = webdriver.find_element_by_name('q')
# search_box.send_keys('ChromeDriver')
# search_box.submit()

time.sleep(sleep_time) 
webdriver.quit()
