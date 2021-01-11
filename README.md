# EPS račun - Electric bill (Serbian)

### Namena:

- Skini poslednji račun za struju, za fizička lica sa portala:

http://portal.edb.rs

- Smesti PDF račun u data/ subfolder.

- Zapamti koji je poslednji skinuti račun, u storage.yaml

- Ako nema novog računa, završi program.

- Ako je došlo do greške u parsiranju web stranice, ispiši problem na stdout i izađi sa statusnim kodom 1.

### Instalacija:

- Potreban je prethodno instaliran Python 3.6+

- Instaliraj module iz requirements.txt:

```
pip install -r requirements.txt
```

- Preimenuj config.yaml.DEFAULT u config.yaml

- Edituj config.yaml i upiši svoje ime i šifru.

### Platforme:

- Radi na Linux x64, Windows x64 i Raspbian arm7hf platformama.

- Za MacOS, prouči rešenje problema notarizacije:

https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html
