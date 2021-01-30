"""
Browser module, as Selenium wrapper
"""


import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


def firefox(config):
    """
    Start browser with disabled "Save PDF" dialog
    Download files to var folder
    """
    my_options = Options()
    if config.headless:
        my_options.headless = True
        my_options.add_argument('--window-size=1920,1200')
    my_profile = webdriver.FirefoxProfile()
    my_profile.set_preference('general.useragent.override', config.user_agent)
    my_profile.set_preference('browser.download.folderList', 2)
    my_profile.set_preference('browser.download.manager.showWhenStarting', False)
    my_profile.set_preference('browser.download.manager.useWindow', False)
    my_profile.set_preference('pdfjs.disabled', True)
    my_profile.set_preference('browser.download.dir',
                              os.path.join(os.getcwd(), 'var'))
    my_profile.set_preference('browser.helperApps.neverAsk.openFile',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')
    my_profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')
    driver = webdriver.Firefox(executable_path=config.gecko_path(), options=my_options, firefox_profile=my_profile)
    driver.implicitly_wait(config.timeout)
    return driver


def find_first_by_id(browser, target):
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


def find_first_by_css(browser, target):
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


def find_all_by_css(browser, target):
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


def remove_element_by_css(browser, target):
    """
    Locate element by CSS selector, and remove it from DOM, with JavasScript code
    """
    browser.execute_script(f"""
    var element = document.querySelector("{target}");
    if (element)
        element.parentNode.removeChild(element);
    """)


def screenshot_browser_windows(browser, file):
    """
    Take screenshot of visible browser window and save as file
    Works in headless mode to
    """
    browser.get_screenshot_as_file(file)


def screenshot_full_page(browser, file):
    """
    Take screenshot of full page and save as file
    Works ONLY in headless mode
    """
    S = lambda X: browser.execute_script('return document.body.parentNode.scroll' + X)
    browser.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
    browser.find_element_by_tag_name('body').screenshot(file)
