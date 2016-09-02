#!/usr/bin/env python
import logging
import time
import traceback
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    filename="scrawl.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s@%(filename)s - %(levelname)s: %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.log

sys.setrecursionlimit(1500)
driver = webdriver.Firefox()

url = sys.argv[3]
username = sys.argv[1]
password = sys.argv[2]
visited_url_file ='visted_urls.log'

visited_urls = []
broken_urls = []
slow_urls = []

broken_url_log = "404s_scrawl.log"
slow_url_log = "slowpages_scrawl.log"

def wait(driver,
        locator_string,
        max_duration=5,
        condition=EC.element_to_be_clickable,
        locator=By.CSS_SELECTOR):
    return WebDriverWait(driver, max_duration).until(condition((locator, locator_string)))

def wait_for_logo(driver, link):
    try:
        if 'support' not in driver.current_url:
            return wait(
                driver=driver,
                locator_string='a[href="https://logrhythm.com"]',
                locator=By.CSS_SELECTOR
                )
        return wait(driver=driver, locator_string="logo", locator=By.ID)
    except:
        slow_urls.append(link)
        append_to_file(slow_url_log, link)
        log(logging.WARNING, "Identified slow link: " + str(link))

def append_to_file(filename, url):
    with open(filename, "a+") as f:
        f.write(str(url) + '\n')

def get_visited_urls(fp):
    ret = []
    with open(fp, 'a+') as visited:
        ret = [x.strip() for x in visited.readlines()]
    return ret


def login(url, username, password, driver):
    driver.get(url)
    elem = driver.find_element_by_name('email')
    elem.send_keys(username)
    elem_pass = driver.find_element_by_name('password')
    elem_pass.send_keys(password)
    elem_login = driver.find_element_by_class_name('formButton')
    elem_login.click()

def recursive_link_finder(driver, links):
    if not links:
        return
    for link in links:
        if not link:
            continue
        if link not in get_visited_urls(visited_url_file) and 'logrhythm.com' in link and 'mailto:' not in link:
            driver.get(link)
            log(logging.INFO, "Visited: " + str(link))
            wait_for_logo(driver, link)
            if driver.current_url == 'https://logrhythm.com/404/':
                broken_urls.append(link)
                append_to_file(broken_url_log, link)
                log(logging.INFO, link)
                log(logging.WARNING, "Identified broken link: " + str(link))
            sub_links = [x.get_attribute('href') for x in driver.find_elements_by_tag_name('a')]
            append_to_file(visited_url_file, link)
            recursive_link_finder(driver, sub_links)

if __name__ == '__main__':
    try:
        login(url, username, password, driver)
        current_page = driver.current_url
        links = [x.get_attribute('href') for x in driver.find_elements_by_tag_name('a')]
        recursive_link_finder(driver, links)
            
    except Exception as e:
        log(logging.ERROR, traceback.format_exc())
    finally:
        print "SLOW LINKS:"
        print slow_urls
        print "\nBROKEN LINKS: "
        print broken_urls
        driver.quit()
