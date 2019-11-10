from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import time

def hover_on_element(browser, element):
    Hover = ActionChains(browser).move_to_element(element)
    try:
        Hover.click().perform()
        return True
    except:
        return False

browser = webdriver.Firefox(executable_path='/home/amuktha/headrun/geckodriver')
browser.get("https://platform.application.prd.supplyon.com/logon/logonServlet") 
time.sleep(5)
username = browser.find_element_by_id("j_username")
password = browser.find_element_by_id("j_password")
username.send_keys("iWA_PGB")
time.sleep(2)
password.send_keys("Pump@123#")
time.sleep(2)
login_attempt = browser.find_element_by_id("j_submit")
login_attempt.submit()
time.sleep(20)
supplyon_tab = browser.find_element_by_xpath('//div[contains(text(), "SupplyOn Services")]')
hover_res = hover_on_element(browser, supplyon_tab)
if not hover_res:
    print "hover on supplyon tab failed"
    
time.sleep(2)
supplyon_webedi_tab = browser.find_element_by_xpath('//div[contains(text(), "WebEDI / VMI")]')
supplyon_webedi_tab.click()
time.sleep(10)


length_of_iframe = len(browser.find_elements_by_tag_name("iframe"))
if length_of_iframe == 2:
    browser.switch_to_frame(1)
    time.sleep(10)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

    if "102MenuImg" in browser.page_source:
        asn_hover = browser.find_element_by_id("102MenuImg")
        Hover = ActionChains(browser).move_to_element(asn_hover)
        Hover.perform()
        #x = browser.find_element_by_xpath('//a[contains(@onclick, "asn_overview")]/../..')
        time.sleep(5)
        import pdb;pdb.set_trace()
        x = browser.find_element_by_xpath('//a[contains(@href, "asn_create")]')
        x.click()
        if False:
            #x = browser.find_element_by_xpath('//*[text()[contains(., "Create ASN")]]/..')
            x = browser.find_element_by_xpath('//a[contains(@href, "asn_create")]')
            x.click()

time.sleep(5)
import pdb;pdb.set_trace()


browser.close()
