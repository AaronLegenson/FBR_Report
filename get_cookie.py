# -*- coding: utf-8 -*-

import sys
import os
import platform
import time
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from strings import *


def chrome_driver(url, headless, chromedriver_path):
    chrome_options = webdriver.ChromeOptions()  # Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    if headless:
        chrome_options.add_argument(STRING_CHROME_OPTION_HEADLESS)
    if chromedriver_path is None:
        chromedriver_path = STRING_FORMAT_7.format(
            sys.path[0], os.sep, STRING_CHROMEDRIVER, os.sep, platform.system().lower(), os.sep, STRING_CHROMEDRIVER)
    driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
    driver.maximize_window()
    driver.implicitly_wait(3)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    try:
        driver.get(url)
    except Exception as e:
        print("Error in loading page too slow:", e)
        driver.execute_script("window.stop()")
    return driver


def get_cookie(url, username, password, headless=True, chromedriver_path=None):
    driver = chrome_driver(url, headless, chromedriver_path)
    driver.execute_script('document.getElementsByClassName("%s")[0].value="%s";' % (STRING_LOGIN_USERNAME_CLASS, username))
    # driver.find_element_by_class_name(STRING_LOGIN_USERNAME_CLASS).click()
    # driver.find_element_by_class_name(STRING_LOGIN_USERNAME_CLASS).clear()
    # driver.find_element_by_class_name(STRING_LOGIN_USERNAME_CLASS).send_keys(username)
    driver.execute_script('document.getElementsByClassName("%s")[0].value="%s";' % (STRING_LOGIN_PASSWORD_CLASS, password))
    # driver.find_element_by_class_name(STRING_LOGIN_PASSWORD_CLASS).click()
    # driver.find_element_by_class_name(STRING_LOGIN_PASSWORD_CLASS).clear()
    # driver.find_element_by_class_name(STRING_LOGIN_PASSWORD_CLASS).send_keys(password)
    driver.find_element_by_class_name(STRING_LOGIN_BUTTON_CLASS).click()
    cookie_items = driver.get_cookies()
    cookie_str = STRING_EMPTY
    for item_cookie in cookie_items:
        item_str = STRING_FORMAT_COOKIE.format(item_cookie[STRING_NAME], item_cookie[STRING_VALUE])
        cookie_str += item_str
    driver.quit()
    return cookie_str


if __name__ == "__main__":
    res = get_cookie("https://oa.fusionfintrade.com/", "yunying_hook", "Juliang123$%", True)
    print(res)
