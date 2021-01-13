#!/usr/bin/env python3
"""
Skini poslednji račun za struju, za fizička lica:
portal.edb.rs

Username i šifra su u config.yaml.

Smesti PDF račun u pdf subfolder.
Zapamti koji je poslednji skinuti račun, u data/storage.yaml
Ako nema novog računa, završi program.
Ako je došlo do promena u sajtu, ispiši problem na stderr i izađi sa statusnim kodom 1
"""


import os
import platform
import sys
import shutil
import yaml
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


class Config:
    """
    Configuration, from config.yaml
    """
    def __init__(self):
        with open('config.yaml') as f:
            cfg = yaml.full_load(f)
        self.accounts = cfg['accounts']
        self.url = cfg['url']
        self.headless = cfg['headless']
        self.user_agent = cfg['user_agent']


class Storage:
    """
    Storage
    """
    def __init__(self, user):
        self.file_path = f'data/storage_{user}.yaml'
        if os.path.isfile(self.file_path):
            with open(self.file_path) as fin:
                my_storage = yaml.full_load(fin)
            self.last_period = my_storage['last_period']
        else:
            self.last_period = 'none'

    def write(self):
        my_storage = {'last_period': self.last_period}
        with open(self.file_path, 'w') as fout:
            yaml.dump(my_storage, fout)


def find_first_id(browser, target):
    try:
        element = browser.find_element_by_id(target)
        return element
    except NoSuchElementException:
        print(f"Can't find id: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def find_first_css(browser, target):
    try:
        element = browser.find_element_by_css_selector(target)
        return element
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def find_all_css(browser, target):
    try:
        elements = browser.find_elements_by_css_selector(target)
        return elements
    except NoSuchElementException:
        print(f"Can't find CSS selector: {target}", file=sys.stderr)
        browser.quit()
        sys.exit(1)


def gecko_path():
    my_system = platform.system()
    my_machine = platform.machine()
    if my_system == 'Linux' and my_machine == 'x86_64':
        # Linux PC
        exe_path = r'bin/linux64/geckodriver'
    elif my_system == 'Linux' and my_machine == 'armv7l':
        # Linux Raspberry Pi
        exe_path = r'bin/arm7hf/geckodriver'
    elif my_system == "Windows":
        # Windows
        exe_path = r'bin/win64/geckodriver.exe'
    elif my_system == "Darwin":
        # Mac
        # Notarization Workaround:
        # https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html
        exe_path = r'bin/macos/geckodriver'
    else:
        # No idea
        print(f"Unknown OS: {my_system}/{my_machine}", file=sys.stderr)
        sys.exit(1)

    return exe_path


def start_browser(cfg):
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

    return webdriver.Firefox(executable_path=gecko_path(), options=my_options, firefox_profile=my_profile)


def move_and_rename_pdf(user):
    # TODO use alias and YYYYMM for PDF file name
    for pdf_file in Path('data').glob('**/*.pdf'):
        new_path = 'pdf/' + user + '_' + pdf_file.stem + '.pdf'
        shutil.move(pdf_file, new_path)


if __name__ == '__main__':
    config = Config()

    for account in config.accounts:
        username = str(account['username'])
        password = str(account['password'])
        if username == 'None':
            continue
        storage = Storage(username)

        # Start browser
        driver = start_browser(config)

        # Load page
        try:
            driver.get(config.url)
        except Exception as e:
            print('Error loading page', file=sys.stderr)
            driver.quit()
            sys.exit(1)

        # Login
        login_name = find_first_id(driver, 'j_username')
        login_name.send_keys(username)
        login_password = find_first_id(driver, 'j_password')
        login_password.send_keys(password)
        login_button = find_first_id(driver, 'cbPrihvati')
        login_button.click()

        # Choose: Main page > Računi
        choose_racuni = find_first_css(driver, 'a[title="Pregled računa"]')
        choose_racuni.click()

        # Invoices table
        invoices = find_all_css(driver, 'table.x2f tbody tr')
        # Skip first row [0] as header
        # Last period is in second cell of second row [1]
        if len(invoices) > 1:
            last_invoice = invoices[1]
            period = find_first_css(last_invoice, 'td:nth-child(2)').text.strip()
        else:
            print("Can't find table with invoices", file=sys.stderr)
            driver.quit()
            sys.exit(1)

        # Anything new?
        last_period = storage.last_period.strip()
        if period != last_period:
            print(f'{username} - {period}')
            # Save PDF with click on last cell in row 1
            save_button = find_first_css(invoices[1], 'td:last-child')
            save_button.click()
            # Save period as last_period in storage.yaml
            storage.last_period = period
            storage.write()
            # Move PDF file from data to pdf folder
            move_and_rename_pdf(username)

        # Logout
        logout_button = find_first_css(driver, 'a[title="Odjavljivanje sa sistema"]')
        logout_button.click()
        # TODO don't quit browser ater every account, just at the end of the program
        driver.quit()
