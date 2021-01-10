#!/usr/bin/env python3
"""
Pregled računa za struju, za fizička lica:
portal.edb.rs
"""


import os
import platform
import sys
import yaml
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


def find_first_id(browser, target):
    try:
        element = browser.find_element_by_id(target)
        return element
    except NoSuchElementException:
        print(f"Can't find id: {target}")
        browser.quit()
        sys.exit(1)


def find_first_css(browser, target):
    try:
        element = browser.find_element_by_css_selector(target)
        return element
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}")
        browser.quit()
        sys.exit(1)


def find_all_css(browser, target):
    try:
        element = browser.find_elements_by_css_selector(target)
        return element
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}")
        browser.quit()
        sys.exit(1)


def gecko_path():
    my_system = platform.system()
    my_machine = platform.machine()
    exe_path = ''
    if my_system == 'Linux':
        if my_machine == 'x86_64':
            # Linux PC
            exe_path = r'bin/linux64/geckodriver'
        elif my_machine == 'armv7l':
            # Linux Raspberry Pi
            exe_path = r'bin/arm7hf/geckodriver'
        else:
            # No idea
            pass
    elif my_system == "windows":
        # Windows
        execpath = r'bin/win64/geckodriver.exe'
    elif my_system == "darwin":
        # Mac
        pass
    else:
        # No idea
        pass
    return exe_path


def start_browser(cfg):
    my_options = Options()
    if cfg['headless']:
        my_options.headless = True
        my_options.add_argument(cfg['headless_window_size'])
    my_profile = webdriver.FirefoxProfile()
    my_profile.set_preference('general.useragent.override', cfg['user_agent'])
    my_profile.set_preference('browser.download.folderList', 2)
    my_profile.set_preference('browser.download.manager.showWhenStarting', False)
    my_profile.set_preference('browser.download.manager.useWindow', False)
    my_profile.set_preference('pdfjs.disabled', True)
    my_profile.set_preference('browser.download.dir',
                              os.path.join(os.getcwd(), cfg['download_dir']))
    my_profile.set_preference('browser.helperApps.neverAsk.openFile',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')
    my_profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                              'application/octet-stream, application/pdf, application/x-www-form-urlencoded')

    return webdriver.Firefox(executable_path=gecko_path(), options=my_options, firefox_profile=my_profile)


with open('config.yaml') as f:
    CONFIG = yaml.full_load(f)
if os.path.isfile('storage.yaml'):
    with open('storage.yaml') as f:
        STORAGE = yaml.full_load(f)
else:
    STORAGE = {'last_period': 'none'}

driver = start_browser(CONFIG)

# Load URL
try:
    driver.get(CONFIG['url'])
except Exception as e:
    print('Error loading page')
    driver.quit()
    sys.exit(1)

# Login
login_name = find_first_id(driver, 'j_username')
login_name.send_keys(CONFIG['username'])
login_password = find_first_id(driver, 'j_password')
login_password.send_keys(CONFIG['password'])
login_button = find_first_id(driver, 'cbPrihvati')
login_button.click()

# Main page > Računi
choose_racuni = find_first_css(driver, 'a[title="Pregled računa"]')
choose_racuni.click()

# Table, skip first row [0] as header
invoices = find_all_css(driver, 'table.x2f tbody tr')
# Last period is in second cell of first row
if len(invoices) > 1:
    last_invoice = invoices[1]
    period = find_first_css(last_invoice, 'td:nth-child(2)').text.strip()
else:
    print("Can't find table with invoices")
    driver.quit()
    sys.exit(1)

# Anything new?
last_period = STORAGE['last_period'].strip()
if period != last_period:
    print(period)
    # Save PDF
    save_button = find_first_css(invoices[1], 'td:last-child')
    save_button.click()
    # Save period as last_period in storage.yaml
    STORAGE['last_period'] = period
    with open('storage.yaml', 'w') as f:
        yaml.dump(STORAGE, f)

# Logout
logout_button = find_first_css(driver, 'a[title="Odjavljivanje sa sistema"]')
logout_button.click()
driver.quit()
