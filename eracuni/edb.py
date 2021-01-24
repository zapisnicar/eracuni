"""
EPS Beograd
"""


import sys
from eracuni.data import Storage
from eracuni.browser import find_first_id, find_first_css, find_all_css


class Edb:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

        for account in self.config.edb_accounts:
            storage = Storage(f'edb_{account.alias}')

            # Load page
            try:
                self.driver.get(self.config.edb_url)
            except Exception as e:
                print('Error loading page', file=sys.stderr)
                self.driver.quit()
                sys.exit(1)

            # Login
            login_name = find_first_id(self.driver, 'j_username')
            login_name.send_keys(account.user_id)
            login_password = find_first_id(self.driver, 'j_password')
            login_password.send_keys(account.password)
            login_button = find_first_id(self.driver, 'cbPrihvati')
            login_button.click()

            # Choose Računi from menu
            menu_racuni = find_first_css(self.driver, 'a[title="Pregled računa"]')
            menu_racuni.click()

            # Find Invoices table
            invoices = find_all_css(self.driver, 'table.x2f tbody tr')
            # Skip first row [0] as header
            # Last period is in second cell of second row [1]
            if len(invoices) > 1:
                last_invoice = invoices[1]
                period = find_first_css(last_invoice, 'td:nth-child(2)').text.strip()
            else:
                print("Can't find table with invoices", file=sys.stderr)
                self.driver.quit()
                sys.exit(1)

            # Anything new?
            if period != storage.last_saved:
                print(f'storage_edb_{account.alias} - {period}')
                # Save PDF with click on last cell in row 1
                save_button = find_first_css(invoices[1], 'td:last-child')
                save_button.click()
                # Move saved PDF file from data to pdf folder
                storage.move_pdf()
                # Save period in self.storage.yaml
                storage.last_saved = period

            # Logout
            logout_button = find_first_css(self.driver, 'a[title="Odjavljivanje sa sistema"]')
            logout_button.click()
