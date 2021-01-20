"""
Browser module, as Selenium wrapper
"""


import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


def find_first_id(browser, target):
    """
    Locate web element by id attribute
    Return first one
    Catch No Such Element Exception error, report problem to stderr and quit with exit code 1
    """
    try:
        element = browser.find_element_by_id(target)
        return element
    except NoSuchElementException:
        print(f"Can't find id: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def find_first_css(browser, target):
    """
    Locate web element by css selector
    Return first one
    Catch No Such Element Exception error, report problem to stderr and quit with exit code 1
    """
    try:
        element = browser.find_element_by_css_selector(target)
        return element
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def find_all_css(browser, target):
    """
    Locate all web elements by css selector
    Return list of elements
    Catch No Such Element Exception error, report problem to stderr and quit with exit code 1
    """
    try:
        elements = browser.find_elements_by_css_selector(target)
        return elements
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def start(cfg):
    """
    Start browser with disabled "Save PDF" dialog
    Download files to data folder
    """
    my_options = Options()
    if cfg.headless:
        my_options.headless = True
        my_options.add_argument('--window-size=1920,1200')
    my_profile = webdriver.FirefoxProfile()
    my_profile.set_preference('general.useragent.override', cfg.user_agent)
    my_profile.set_preference('browser.download.folderList', 2)
    my_profile.set_preference('browser.download.manager.showWhenStarting', False)
    my_profile.set_preference('browser.download.manager.useWindow', False)
    my_profile.set_preference('pdfjs.disabled', True)
    my_profile.set_preference('browser.download.dir',
                              os.path.join(os.getcwd(), 'data'))
    my_profile.set_preference('browser.helperApps.neverAsk.openFile',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')
    my_profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')

    return webdriver.Firefox(executable_path=cfg.gecko_path, options=my_options, firefox_profile=my_profile)