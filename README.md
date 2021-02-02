# Račundžija - Utility bills scraper (Serbian)

- EPS (Beograd) i InfoStan računi

### Kako radi:

- Pronađi poslednje račune sa EDB i Infostan portala:
  
    http://portal.edb.rs

    https://esanduce.rs

- Ako nema novog računa, završi program.
  
- Ako ima, snimi račun u pdf folder i pošalji obaveštenje na eMail/Telegram.

- Zapamti koji je poslednji skinuti račun, u var/storage.yaml

- Ako je došlo do greške u parsiranju web stranice, ispiši problem na stderr i izađi sa statusnim kodom 1.

### Instalacija:

- Potrebni su prethodno instalirani Python 3.6+ i Firefox, primer za Linux:

```
sudo apt update
sudo apt install python3 python3-dev python3-venv
sudo apt install firefox-esr
```

- Preuzmi program sa ove stranice kao zip arhivu i otpakuj je u željeni folder. Ili koristi git:

```
git clone https://github.com/zapisnicar/eracuni
```

- Instaliraj neophodne module:

```
pip3 install -r requirements.txt
    ili
pip install -r requirements.txt
```

- Preimenuj config.yaml.DEFAULT u config.yaml

- Edituj config.yaml i upiši svoj ID, šifru i opciono alijas. Može se koristiti proizvoljan broj naloga. Moraju biti u YAML formatu, a neaktivni nalozi trebaju ili da se obrišu ili da imaju prazan string za username. Alijas će se koristiti kao prefiks pri snimanju fajlova, recimo "stan" ili "garaza". Mora biti jedinstven. Po želji, konfiguriši eMail i Telegram. Savete za pravljenje Telegram bota pročitaj ovde: 

https://gist.github.com/zapisnicar/247d53f8e3980f6013a221d8c7459dc3

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

- U bin folderu se nalaze Firefox geckodriver programi za razne platforme, koji su preuzeti sa:

https://github.com/mozilla/geckodriver/releases