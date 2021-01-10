#!/usr/bin/env python3
"""
Pregled računa za struju, za fizička lica:
portal.edb.rs
"""


import os
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


with open('config.yaml') as f:
    CONFIG = yaml.full_load(f)
with open('storage.yaml') as f:
    STORAGE = yaml.full_load(f)


my_options = Options()
if CONFIG['headless']:
    my_options.headless = True
    my_options.add_argument(CONFIG['headless_window_size'])
my_profile = webdriver.FirefoxProfile()
my_profile.set_preference('general.useragent.override', CONFIG['user_agent'])
my_profile.set_preference('browser.download.folderList', 2)
my_profile.set_preference('browser.download.manager.showWhenStarting', False)
my_profile.set_preference('browser.download.manager.useWindow', False)
my_profile.set_preference('pdfjs.disabled', True)
my_profile.set_preference('browser.download.dir',
                          os.path.join(os.getcwd(), CONFIG['download_dir']))
my_profile.set_preference('browser.helperApps.neverAsk.openFile',
                          'application/octet-stream, application/pdf, application/x-www-form-urlencoded')
my_profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                          'application/octet-stream, application/pdf, application/x-www-form-urlencoded')


driver = webdriver.Firefox(options=my_options, firefox_profile=my_profile)
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