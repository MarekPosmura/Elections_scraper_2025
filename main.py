"""
Election Scraper - třetí projekt do Engeto Online Python Akademie

Author: Marek Pošmura
Email: m.posmuara@seznam.cz
"""
import csv
import sys
from urllib.parse import parse_qs, urljoin, urlparse

import requests
import validators
from bs4 import BeautifulSoup
from tqdm import tqdm

# NAČTENÍ ARGUMENTŮ
def zpracuj_argumenty():
    """Zkontroluje a načte vstupní argumenty programu."""
    if len(sys.argv) != 3:
        print("Chyba: Musíte zadat 2 argumenty! \nZadejte: python skript.py 'platná URL' 'název_souboru.csv'")
        sys.exit("Ukončuji program!")

    vstupni_url = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    # Kontrola, zda je URL platná
    if not validators.url(vstupni_url):
        print("Chyba: První argument musí být platná URL adresa!")
        sys.exit("Ukončuji program!")

    # Kontrola, zda má soubor příponu .csv
    if not vystupni_soubor.endswith(".csv"):
        print("Chyba: Druhý argument musí být CSV soubor (např. vysledky.csv)!")
        sys.exit("Ukončuji program!")
    return vstupni_url, vystupni_soubor

# STAHOVÁNÍ DAT
def parsuj_html(odkaz):
    """Stáhne HTML z dané URL a vrátí objekt BeautifulSoup."""
    try:
        odpoved = requests.get(odkaz)
        odpoved.raise_for_status()  # Ověří, že nedošlo k HTTP chybě
        soup = BeautifulSoup(odpoved.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Chyba při stahování stránky: {e}")
        return None  # Vrátí None, pokud nastane chyba

def stahni_odkazy_url(url):
    """Stáhne veškeré požadované odkazy z URL stránky."""
    soup = parsuj_html(url)
    odkazy = soup.find_all("a")
    platne_odkazy = []

    for odkaz in odkazy:
        href = odkaz.get("href")  # Získání URL odkazu
        if href and "ps311" in href:
            upraveny_odkaz = uprav_absolutni_cestu_odkazu(href)

            # Kontrola duplicity po úpravě odkazu
            if upraveny_odkaz not in platne_odkazy:
                platne_odkazy.append(upraveny_odkaz)
    return platne_odkazy

def uprav_absolutni_cestu_odkazu(odkaz):
    """Relativní URL adrese transformuje na absolutní URL adresu."""
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    return urljoin(base_url, odkaz)

# ZPRACOVÁNÍ ÚDAJŮ OBCE
def uloz_kod_obce(odkaz_obce):
    """Extrahuje číslo obce z URL adresy."""
    parsed_url = urlparse(odkaz_obce) # parsuje URL adresu >>  Rozdělí URL na části (protokol, doménu, cestu, parametry atd.).
    query_params = parse_qs(parsed_url.query) # Převede dotazovací řetězec na slovník s parametry a jejich hodnotami.
    return query_params.get("xobec", [None])[0] # Bezpečně získá hodnotu parametru xobec >>> tedy číslo obce

def uloz_nazev_obce(soup):
    """Najde a vrátí název obce v požadovaném formátu."""
    if soup:
        try:
            nadpis_obce = soup.find_all("h3")[2].text.strip().replace("Obec: ", "")
            return nadpis_obce
        except IndexError:
            print("Nepodařilo se najít název obce.")
            return None
    return None

def uloz_udaje_obce(odkaz_obce):
    """Stáhne a zpracuje informace o jedné obci"""
    soup = parsuj_html(odkaz_obce)
    if not soup:
        return None  # Pokud selže stahování, vrátíme None

    kod_obce = uloz_kod_obce(odkaz_obce)
    obec = uloz_nazev_obce(soup)
    tabulky = uloz_tabulky_na_strance(soup)

    return kod_obce, obec, tabulky

# ZPRACOVÁNÍ VOLEBNÍCH VÝSLEDKŮ
def uloz_tabulky_na_strance(soup):
    """Uloží veškeré tabulky na stránce do seznamu."""
    if soup:
        tabulky = soup.find_all("table")  # Najde všechny tabulky na stránce
        return tabulky
    return []  # Pokud se stránka nenačte, vrátí prázdný seznam

def zpracuj_vysledky_hlasovani(soup):
    """Zpracuje informace o hlasování u jedné obce."""
    tabulky = uloz_tabulky_na_strance(soup)
    if len(tabulky) < 3:
        return print("Nedostatečný počet tabulek")
    souhrnne_udaje = zpracuj_souhrnne_udaje(tabulky[0])
    hlasovani_stran = (
        uloz_udaje_politickych_stran(tabulky[1]) +
        uloz_udaje_politickych_stran(tabulky[2])
    )
    return souhrnne_udaje, hlasovani_stran

def zpracuj_souhrnne_udaje(souhrnna_tabulka):
    """Zpracuje údaje ze souhrnné tabulky. Výstupem je seznam slovníků."""
    if souhrnna_tabulka is None:
        print("Chyba: Žádná tabulka nebyla nalezena.")
        return []

    vsechny_tr = souhrnna_tabulka.find_all("tr")
    if len(vsechny_tr) < 3:
        print("Chyba: Očekávaný řádek v tabulce neexistuje.")
        return []

    tr = vsechny_tr[2]  # požadovaný řádek
    td_bunky = tr.find_all("td")

    if len(td_bunky) < 9:
        print("Chyba: Tabulka nemá dostatek buněk.")
        return []

    # Seznam slovníků – každý slovník obsahuje jen jeden údaj
    # replace("\xa0", "") - odstraní mezery v číslech, které místo čísla vytvářejí string
    udaje_list = [
        {"volebni_ucast_%": td_bunky[5].get_text(strip=True).replace("\xa0", "")},
        {"volici_v_seznamu": int(td_bunky[3].get_text(strip=True).replace("\xa0", ""))},
        {"vydane_obalky": int(td_bunky[4].get_text(strip=True).replace("\xa0", ""))},
        {"odevzdane_obalky": int(td_bunky[6].get_text(strip=True).replace("\xa0", ""))},
        {"platne_hlasy": int(td_bunky[7].get_text(strip=True).replace("\xa0", ""))},
        {"platne_hlasy_%": td_bunky[8].get_text(strip=True).replace("\xa0", "")}
    ]
    return udaje_list

def uloz_udaje_politickych_stran(tabulka):
    """Uloží údaje ohlasování z tabulky. Výstupem je seznam slovníků."""
    seznam_udaju = []

    table_rows = tabulka.find_all("tr")[2:]  # Přeskakujeme první dva řádky (hlavičku)

    for row in table_rows:
        columns = row.find_all("td")
        if len(columns) < 3:  # Ověříme, že tabulka má dostatek sloupců
            continue
        nazev_strany = columns[1].get_text(strip=True)
        pocet_hlasu = int(columns[2].get_text(strip=True).replace("\xa0", ""))
        seznam_udaju.append({nazev_strany: pocet_hlasu})

    return seznam_udaju  # Vrací seznam slovníků

# HLAVNÍ SCRAPER FUNKCE
def scraper_dat(url):
    """Funkce pro získání a zpracování výsledků z dané URL."""
    print(f"STAHUJI DATA Z VYBRANÉ URL:\n{url}")
    odkazy = stahni_odkazy_url(url)

    vysledky = []

    for odkaz in tqdm(odkazy, desc="CELKEM STAŽENO", bar_format="{l_bar}{bar:30}{n_fmt}/{total_fmt} ODKAZŮ"): # tqdm - funkce pro vizualizaci průběhu stahování (progres bar)
        udaje_o_obci = uloz_udaje_obce(odkaz)
        if udaje_o_obci:
            soup = parsuj_html(odkaz)
            kod_obce, obec, tabulky = udaje_o_obci  # Rozbalení návratových hodnot

            souhrnne_udaje, hlasovani_stran = zpracuj_vysledky_hlasovani(soup)

            # Vytvoření slovníku s údaji o obci
            obec_data = {"kod_obce": kod_obce, "obec": obec}

            # Převod seznamů slovníků na jeden slovník
            for udaj in souhrnne_udaje:
                obec_data.update(udaj)  # Přidání souhrnných údajů do slovníku

            for strana in hlasovani_stran:
                obec_data.update(strana)  # Přidání údajů o politických stranách

            vysledky.append(obec_data)

    return vysledky

def ziskej_volebni_data(url, nazev_vystupniho_csv_souboru):
    """Hlavní program, který stahuje a zpracovává data
    ze zadané URL adresy, který poté data vyexportuje do csv souboru."""
    data = scraper_dat(url)
    export_do_csv(data, nazev_vystupniho_csv_souboru)

# EXPORT DO CSV
def export_do_csv(data, vystupni_soubor):
    """Export získaných dat do CSV souboru."""
    if not data:
        print("Chyba: Nebyla nalezena žádná data pro export!")
        return
    print(f"UKLÁDÁM DATA DO SOUBORU: {vystupni_soubor}")
    # byl použit encoding="utf-8-sig" namísto "utf-8", při kterém se chybně zobrazovala diakritika při otevření v MS EXCEL
    with open(vystupni_soubor, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        fieldnames = data[0].keys()  # Získá názvy sloupců z klíčů slovníků
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)  # Zapíše všechny řádky
    print(f"PROGRAM ÚSPEŠNĚ VYTVOŘIL CSV SOUBOR.")

# HLAVNÍ FUNKCE
if __name__ == "__main__":
    vstupni_url, vystupni_soubor = zpracuj_argumenty()
    ziskej_volebni_data(vstupni_url, vystupni_soubor)
    print(f"UKONČUJI PROGRAM ELECTION SCRAPER.")