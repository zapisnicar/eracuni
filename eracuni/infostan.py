"""
InfoStan
"""


import sys
from eracuni.data import Storage
from eracuni.browser import find_first_id, find_first_css, find_all_css
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
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
            icon_infostan = find_first_id(self.driver, '1_ЈКП Инфостан Технологије')
            icon_infostan.click()

            # Find all locations
            number_of_locations = len(find_all_css(self.driver, 'div.row-item'))
            for i in range(1, number_of_locations + 1):
                # Choose location
                row = find_first_css(self.driver,
                                     f'.container-page > div:nth-child(4) > div:nth-child({i}) > div:nth-child(1)')
                row.click()
                # Find top row, with last bill
                last_row = find_first_css(self.driver, 'div.row-item')
                last_period_cell = find_first_css(last_row, '.rowItemName > a')
                print(last_period_cell.get_attribute('text'))
                # Click on top row, for side menu
                last_row.click()
                # Find "Pregled računa" button
                pregled_racuna_button = find_first_id(driver, 'step5')
                pregled_racuna_button.click()
                # Wait until page load
                WebDriverWait(driver, self.config.timeout).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div.page[data-loaded="true"')))
                # Find Download icon
                save_button = find_first_id(driver, 'download')
                save_button.click()
                # Wait 1 sec
                time.sleep(1)
                # Find (X) - Close button
                close_button = find_first_css(driver, 'div.pdfCloseBtn>span.close-btn')
                close_button.click()
                # Find back button
                back_button = find_first_css(driver, 'div.icon-back')
                back_button.click()

            print('End of program')
            time.sleep(10)


