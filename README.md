# Projekt č. 3 – Election Scraper

## 📌 Popis programu  
**Election Scraper** je program pro stahování a analýzu volebních výsledků z voleb do Poslanecké sněmovny ČR v roce 2017.  
Program získává data o volební účasti, výsledcích politických stran pro jednotlivé obce a exportuje je do souboru **CSV**.

---

## 📦 Instalace knihoven  
Před spuštěním projektu je nutné vytvořit a aktivovat **virtuální prostředí**, ve kterém budou nainstalovány potřebné knihovny.  

### 🛠 Postup:
1. **Otevřete terminál** a přejděte do složky s projektem.
2. **Vytvořte virtuální prostředí**:  
   ```sh
      python -m venv venv

3. **Aktivujte virtuální prostředí**:<br>
      Windows:
    ```sh
      venv\Scripts\activate
    ```
      macOS / Linux:<br>
    ```sh
      source venv/bin/activate

5. **Nainstalujte potřebné knihovny ze souboru requirements.txt**:
      ```sh
      pip install -r requirements.txt

## ▶️ Spuštění programu

Program lze spustit pomocí příkazu v terminálu. Je nutné zadat dva povinné argumenty. Oba argumenty je potřeba ohraničit jednoduchými nebo dvojitými uvozovkami:

   1. Argument: Platná URL stránka požadovaného okresu
   2. Argument: Název výstupního souboru s příponou .csv

🔹 Příklad spuštění:
```sh
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203" "vysledky.csv"
```

## 📊 Ukázka výstupu

Po úspěšném spuštění se zobrazí průběh stahování dat a vytvoří se CSV soubor s volebními výsledky.<br>
Terminálový výstup:
```sh
STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203
CELKEM STAŽENO: 100%      78/78 ODKAZŮ
UKLÁDÁM DATA DO SOUBORU: vysledky.csv
PROGRAM ÚSPĚŠNĚ VYTVOŘIL CSV SOUBOR.
UKONČUJI PROGRAM ELECTION SCRAPER.
```
## 📄 Ukázka výstupu CSV souboru:
```
kod_obce,obec,volebni_ucast_%,volici_v_seznamu,vydane_obalky,odevzdane_obalky,platne_hlasy ...
547786,Adršpach,"59,95",437,262,262,262 ...
573884,Bezděkov nad Metují,"63,45",446,283,283,279 ...
573892,Bohuslavice,"67,93",789,536,536,530 ...
573906,Borová,"68,72",179,123,123,122 ...
...
```
Tento soubor lze otevřít v textovém editoru nebo v Microsoft Excelu pro další analýzu.

ℹ️ Autor: Marek Pošmura
📅 Datum: 27.02.2025
