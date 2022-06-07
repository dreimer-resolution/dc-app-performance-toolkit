from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

datasets = {
    'username': 'admin',
    'password': 'nopassword'
}

sleep_time = 1
url_to_open = "https://jobo-supp-confluence.klab.resolution.de/plugins/servlet/samlsso?idp=4&NameID=admin&redirectTo=%2Fpages%2Fviewpage.action%3FspaceKey%3DMYS%26title%3DSummertime"
# url_to_open = "https://jobo-supp-confluence.klab.resolution.de/plugins/servlet/samlsso?idp=4"

webdriver = webdriver.Chrome()
webdriver.get(url_to_open)

"""
username_inupt = webdriver.find_element_by_xpath(".//*[@id='nameID']")
username_input.clear()
username_input.send_keys(datasets['username'])
webdriver.find_element_by_xpath(".//*[@class='btn btn-default']").click()
"""

WebDriverWait(webdriver, 20) \
    .until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='action-menu-link']"))).click()
WebDriverWait(webdriver, 20) \
    .until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='confluence-export-pdf-menu']"))).click()
WebDriverWait(webdriver, 20) \
    .until(EC.element_to_be_clickable((By.XPATH, ".//*[@class='button-panel-button confluence-export-pdf-export-button']"))).click()

print("done")

webdriver.quit()
