"""
InfoStan Scraper
"""


import sys
import time
from eracuni.data import Storage
from eracuni.browser import find_first_id, find_first_css, find_all_css
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class Infostan:
    def __init__(self, driver, config, notifications):
        self.driver = driver
        self.config = config
        self.notifications = notifications

        for account in self.config.infostan_accounts:
            # Load main page
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

            # Choose Infostan icon
            icon_infostan = find_first_id(self.driver, '1_ЈКП Инфостан Технологије')
            icon_infostan.click()

            # Find number of locations and iterate through them, as i -> (1..n)
            number_of_locations = len(find_all_css(self.driver, 'div.row-item'))
            for i in range(1, number_of_locations + 1):
                # Every location will have unique filename for storage
                storage = Storage(f'infostan_{account.alias}_{i}')

                # Choose location, i-th row in location table
                row_i = find_first_css(
                    self.driver, f'.container-page > div:nth-child(4) > div:nth-child({i}) > div:nth-child(1)')
                row_i.click()

                # Find top row, with last bill
                last_row = find_first_css(self.driver, 'div.row-item')
                last_bill_date = find_first_css(last_row, '.rowItemName > a').get_attribute('text').strip()

                # Anything new?
                if last_bill_date == storage.last_saved:
                    # Nothing new, click on Back button
                    back_button = find_first_css(driver, 'div.icon-back')
                    back_button.click()
                else:
                    # New bill!
                    # Add notification line
                    self.notifications.add(f'InfoStan {account.alias} {i} - {last_bill_date}')

                    # Click on top row, for right side menu
                    last_row.click()
                    # Click on "Pregled računa" button
                    pregled_racuna_button = find_first_id(driver, 'step5')
                    pregled_racuna_button.click()

                    # Wait until page load
                    WebDriverWait(driver, self.config.timeout).until(
                        expected_conditions.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.page[data-loaded="true"')))

                    # Click Download icon
                    save_button = find_first_id(driver, 'download')
                    save_button.click()
                    time.sleep(1)

                    # Click (X) - Close button
                    close_button = find_first_css(driver, 'div.pdfCloseBtn>span.close-btn')
                    close_button.click()

                    # Click Back button
                    back_button = find_first_css(driver, 'div.icon-back')
                    back_button.click()

                    # Move saved PDF file from var to pdf folder
                    storage.move_pdf()

                    # Remember new last_saved in var/storage.yaml
                    storage.last_saved = last_bill_date
                    time.sleep(1)

            # Logout and confirm
            logout_button = find_first_css(driver, 'div.mainBtnsHolder>div:nth-child(7)')
            logout_button.click()
            confirm_button = find_first_css(driver, 'div.modal-delete-action > button:nth-child(1)')
            confirm_button.click()
