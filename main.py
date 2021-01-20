#!/usr/bin/env python3
"""
eRačuni - Utility bills scraper (Serbian)

- Samo za EPS (distributivno područje Beograd) i Infostan

Pronađi poslednje račune za:
- Struju (za fizička lica) sa http://portal.edb.rs
- Infostan sa https://esanduce.rs/

Ako nema novog računa, završi program.
Ako ima, snimi račun u pdf folder.
Zapamti koji je poslednji skinuti račun, u data/storage.yaml
Ako je došlo do greške u parsiranju web stranice, ispiši problem na stderr i izađi sa statusnim kodom 1.
"""


import sys
from eracuni.data import Config, Storage, move_and_rename_pdf
from eracuni.browser import start, find_first_id, find_first_css, find_all_css


def main():
    # Read configuration file
    config = Config()

    # Start browser
    driver = start(config)

    for account in config.edb_accounts:

        storage = Storage(account.alias)

        # Load page
        try:
            driver.get(config.edb_url)
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

        # Find Invoices table
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
