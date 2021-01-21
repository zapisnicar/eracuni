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


from eracuni.data import Config
from eracuni.browser import firefox
from eracuni.edb import Edb
from eracuni.infostan import Infostan


def main():
    # Read configuration file
    config = Config()

    # Start browser
    browser = firefox(config)

    # Check EDB
    Edb(browser, config)

    # Check InfoStan
    Infostan(browser, config)

    # Quit browser
    browser.quit()


if __name__ == '__main__':
    main()
