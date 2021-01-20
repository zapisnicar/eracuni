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
from eracuni.browser import run_firefox
from eracuni.edb import Edb
from eracuni.infostan import Infostan


def main():
    # Read configuration file
    config = Config()

    # Start browser
    driver = run_firefox(config)

    # Check EDB
    Edb(driver, config)

    # Check InfoStan
    Infostan(driver, config)

    # Quit browser
    driver.quit()


if __name__ == '__main__':
    main()
