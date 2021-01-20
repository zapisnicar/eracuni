"""
InfoStan
"""


import sys
from eracuni.data import Storage
from eracuni.browser import find_first_id, find_first_css, find_all_css
import time


class Infostan:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

        for account in self.config.infostan_accounts:
            storage = Storage(account.alias)

            # Load page
            try:
                self.driver.get(self.config.infostan_url)
            except Exception:
                print('Error loading page', file=sys.stderr)
                self.driver.quit()
                sys.exit(1)

            # Login
            login_name = find_first_css(self.driver, "input[formcontrolname='username']")
            login_name.send_keys(account.user_id)
            login_password = find_first_css(self.driver, "input[formcontrolname='password']")
            login_password.send_keys(account.password)
            login_button = find_first_css(self.driver, '.btn-blue')
            login_button.click()

            # Choose Infostan
            time.sleep(2)
            icon_infostan = find_first_id(self.driver, '1_ЈКП Инфостан Технологије')
            icon_infostan.click()

            time.sleep(2)
            x = find_first_css(self.driver, 'div.row-item')
            print(x)
