#!/usr/bin/env python3
"""
EPS račun - Electric bill scraper (Serbian)

- Samo za distributivno područje Beograd

Pronađi poslednji račun za struju (za fizička lica) sa http://portal.edb.rs
Ako nema novog računa, završi program.
Ako ima, snimi račun u pdf folder.
Zapamti koji je poslednji skinuti račun, u data/storage.yaml
Ako je došlo do greške u parsiranju web stranice, ispiši problem na stderr i izađi sa statusnim kodom 1.
"""


import os
import platform
import sys
import shutil
from datetime import date
import yaml
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


class Account:
    """
    Helper class for Config

    Account:
        user_id: string
        password: string
        alias: string
    """
    def __init__(self, user_id, password, alias):
        self.user_id = user_id
        self.password = password
        self.alias = alias


class Config:
    """
    Read configuration file, config.yaml:

    Accounts:           Multiple accounts, list of Account objects
      - user_id:        user id
        password:       user password
        alias:          alias, like home or garage
      - user_id:        other id
        password:       other password
        alias:
      - user_id:
        password:
        alias:
    url:                Login page address
    headless:           To start without GUI or not, True or False
    user_agent:         Browser identifier string

    Accounts with empty user_id are ignored
    If alias is empty, user_id will be used as alias
    There is no limit for how many accounts config file can have
    """
    def __init__(self):
        with open('config.yaml') as f:
            cfg = yaml.full_load(f)
        self.accounts = []
        for user in cfg['accounts']:
            user_id = str(user['user_id']).strip()
            password = str(user['password'])
            alias = str(user['alias']).strip()
            if alias == 'None':
                alias = user_id
            if user_id != 'None':
                self.accounts.append(Account(user_id, password, alias))
        self.url = cfg['url']
        self.headless = cfg['headless']
        self.user_agent = cfg['user_agent']


class Storage:
    """
    Remember what was the last saved PDF bill, by period id string
    Read and write data/storage_{alias}.yaml files, every user_id have separate one
    Use period property as setter/getter
    """
    def __init__(self, alias):
        """
        Read last_period from data/storage_{alias}.yaml
        If does not exist, las_period is "none"
        """
        self.yaml_path = f'data/storage_{alias}.yaml'
        if os.path.isfile(self.yaml_path):
            with open(self.yaml_path) as fin:
                my_storage = yaml.full_load(fin)
            self.__period = my_storage['last_period'].strip()
        else:
            self.__period = 'none'

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, last_period):
        """
        Write data/storage_{alias}.yaml
        """
        self.__period = last_period.strip()
        my_storage = {'last_period': self.__period}
        with open(self.yaml_path, 'w') as fout:
            yaml.dump(my_storage, fout)


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


def gecko_path():
    """
    Return path of geckodriver binary, OS dependent
    """
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
    """
    Start browser with disabled "Save PDF" dialog
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

    return webdriver.Firefox(executable_path=gecko_path(), options=my_options, firefox_profile=my_profile)


def move_and_rename_pdf(alias):
    """
    Rename saved PDF file as {alias}_{YYYY-MM}_{original name}.pdf
    and move it to pdf subfolder
    """
    today = date.today().strftime('%Y-%m')
    for pdf_file in Path('data').glob('**/*.pdf'):
        new_path = f'pdf/{alias}_{today}_{pdf_file.stem}.pdf'
        shutil.move(pdf_file, new_path)


def main():
    # Read configuration file
    config = Config()

    # Start browser
    driver = start_browser(config)

    for account in config.accounts:

        storage = Storage(account.alias)

        # Load page
        try:
            driver.get(config.url)
        except Exception as e:
            print('Error loading page', file=sys.stderr)
            driver.quit()
            sys.exit(1)

        # Login
        login_name = find_first_id(driver, 'j_username')
        login_name.send_keys(account.user_id)
        login_password = find_first_id(driver, 'j_password')
        login_password.send_keys(account.password)
        login_button = find_first_id(driver, 'cbPrihvati')
        login_button.click()

        # Choose Računi from menu
        menu_racuni = find_first_css(driver, 'a[title="Pregled računa"]')
        menu_racuni.click()

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
        if period != storage.period:
            print(f'{account.alias} - {period}')
            # Save PDF with click on last cell in row 1
            save_button = find_first_css(invoices[1], 'td:last-child')
            save_button.click()
            # Move saved PDF file from data to pdf folder
            move_and_rename_pdf(account.alias)
            # Save period in storage.yaml
            storage.period = period

        # Logout
        logout_button = find_first_css(driver, 'a[title="Odjavljivanje sa sistema"]')
        logout_button.click()

    # Quit browser
    driver.quit()


if __name__ == '__main__':
    main()
