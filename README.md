# EPS račun - Electric bill scraper (Serbian)

- Samo za distributivno područje Beograd

### Namena:

- Pronađi poslednji račun za struju (za fizička lica) sa http://portal.edb.rs

- Snimi PDF račun u pdf subfolder.

- Zapamti koji je poslednji skinuti račun, u data/storage.yaml

- Ako nema novog računa, završi program.

- Ako je došlo do greške u parsiranju web stranice, ispiši problem na stdout i izađi sa statusnim kodom 1.

### Instalacija:

- Potreban je prethodno instaliran Python 3.6+ i Firefox

```
sudo apt update
sudo apt install python3 python3-dev python3-venv
sudo apt install firefox-esr
```

- Instaliraj module iz requirements.txt:

```
pip3 install -r requirements.txt
    ili
pip install -r requirements.txt
```

- Preimenuj config.yaml.DEFAULT u config.yaml

- Edituj config.yaml i upiši svoje ime i šifru. Može se koristiti proizvoljan broj naloga. Moraju biti u YAML formatu, a neaktivni nalozi trebaju ili da se obrišu ili da imaju prazan string za username.

- Startuj program sa:

```
python3 main.py
    ili
python main.py
```

### Platforme:

- Radi na Linux x64, Windows x64 i Raspbian arm7hf platformama.

- Za MacOS, prouči rešenje problema notarizacije, nije testirano:

https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html
