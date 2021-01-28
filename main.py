#!/usr/bin/env python3
"""
eRačuni - Utility bills scraper (Serbian)

- EPS (Beograd) i Infostan računi

Pronađi poslednje račune za:
- Struju (za fizička lica) sa http://portal.edb.rs
- Infostan sa https://esanduce.rs/

Ako nema novog računa, završi program.
Ako ima, snimi račun u pdf folder.
Zapamti koji je poslednji skinuti račun, u var/storage.yaml
Ako je došlo do greške u parsiranju web stranice, ispiši problem na stderr i izađi sa statusnim kodom 1.
"""


from eracuni.data import Config
from eracuni.browser import firefox
from eracuni.edb import Edb
from eracuni.infostan import Infostan
from eracuni.messages import Notifications


def main():
    # Read configuration file
    config = Config()
    notifications = Notifications(config)

    # Start browser
    # browser = firefox(config)

    # # Check EDB bills
    # Edb(browser, config)
    #
    # # Check InfoStan bills
    # Infostan(browser, config)
    #
    # # Quit browser
    # browser.quit()

    notifications.send()


if __name__ == '__main__':
    main()
