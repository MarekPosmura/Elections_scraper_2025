"""
election_scraper3.py: třetí projekt do Engeto Online Python Akademie

author: Marek Pošmura
email: m.posmuar@seznam.cz
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import csv
import sys

line = 30 * "-"
line2 = 30 * "#"
# zharaničí dodělat, pokud zbude čas.
# pip freeze > requirements.txt - pro vytvoření souboru s knihovnami, na závěr projektu

# jak zjistit, že je aktivované virtuální prostředí? Do terminálu napsat .venv\Scripts\Activate


# Práce s Gitem - základní postup pro odeslání změn na GitHub
# Při každé změně postupuj takto:

    # git add .                     # přidání všech změn
    # git commit -m "Popis změny"   # commit změn s popisem
    # git push origin main          # odeslání změn na GitHub


########## VSTUPNÍ PARAMETRY ##########
vstupni_url = "https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203" # URL adresa pro okres Náchod 5203 - 78 obcí # pokud se změni "ps2017nss" na "ps2021", tak to vygeneruje výslekdy z roku 2021
vystupni_soubor = "vysledky_nachod.csv"

########## VSTUPNÍ PARAMETRY ##########

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

            ######## Přerušení smyčky po získání 6 odkazů - debugging ########
            if len(platne_odkazy) >= 6:
                break
    return platne_odkazy

def uprav_absolutni_cestu_odkazu(odkaz):
    """Relativní URL adrese transformuje na absolutní URL adresu."""
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    return urljoin(base_url, odkaz)


def uloz_nazev_obce(soup):
    """Najde a vrátí název obce v požadovaném formátu."""
    if soup:
        try:
            nadpis_obce = soup.find_all("h3")[2].text.strip().lstrip("Obec :")
            return nadpis_obce
        except IndexError:
            print("Nepodařilo se najít název obce.")
            return None
    return None

def uloz_kod_obce(odkaz_obce):
    """Extrahuje číslo obce z URL adresy."""
    parsed_url = urlparse(odkaz_obce) # parsuje URL adresu >>  Rozdělí URL na části (protokol, doménu, cestu, parametry atd.).
    query_params = parse_qs(parsed_url.query) # Převede dotazovací řetězec na slovník s parametry a jejich hodnotami.
    return query_params.get("xobec", [None])[0] # Bezpečně získá hodnotu parametru xobec >>> tedy číslo obce

def uloz_udaje_obce(odkaz_obce):
    """Stáhne a zpracuje informace o jedné obci"""
    soup = parsuj_html(odkaz_obce)
    if not soup:
        return None  # Pokud selže stahování, vrátíme None

    kod_obce = uloz_kod_obce(odkaz_obce)
    obec = uloz_nazev_obce(soup)
    tabulky = uloz_tabulky_na_strance(soup)

    return kod_obce, obec, tabulky

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

def uloz_tabulky_na_strance(soup):
    """Uloží veškeré tabulky na stránce do seznamu."""
    if soup:
        tabulky = soup.find_all("table")  # Najde všechny tabulky na stránce
        return tabulky
    return []  # Pokud se stránka nenačte, vrátí prázdný seznam

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

    # Seznam slovníků – každý obsahuje jen jeden údaj
    # replace("\xa0", "") - odstrané mezery v číslech, které způsobují chybu v číslech
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

# ########## TESTY ##########


# pokud bude čas tak dodělat loading bar
# def loading_bar(total_links):
#     for i in range(1, total_links + 1):
#         percent_complete = (i / total_links) * 100

#         # Aktualizace po každých 10 %
#         if percent_complete % 10 == 0 or i == total_links:
#             bar_length = int(percent_complete // 10)  # Počet "█"
#             bar = "█" * bar_length + " " * (10 - bar_length)  # Celková délka 10 znaků

#             sys.stdout.write(f"\rStahování: {bar} {int(percent_complete)}%")
#             sys.stdout.flush()

#     print("\nStahování dokončeno!")



def scraper_dat(url):
    """Funkce pro získání a zpracování výsledků z dané URL."""
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {vstupni_url}")
    odkazy = stahni_odkazy_url(url)

    vysledky = []

    for odkaz in odkazy:
        udaje_o_obci = uloz_udaje_obce(odkaz)
        if udaje_o_obci:
            soup = parsuj_html(odkaz)
            kod_obce, obec, tabulky = udaje_o_obci  # Rozbalení návratových hodnot

            souhrnne_udaje, hlasovani_stran = zpracuj_vysledky_hlasovani(soup)

            # Vytvoření slovníku se všemi daty
            obec_data = {"kod_obce": kod_obce, "obec": obec}

            # Převod seznamů slovníků na jeden slovník
            for udaj in souhrnne_udaje:
                obec_data.update(udaj)  # Přidání souhrnných údajů do slovníku

            for strana in hlasovani_stran:
                obec_data.update(strana)  # Přidání údajů o politických stranách

            vysledky.append(obec_data)

    return vysledky

def election_scraper(url, nazev_vytupniho_csv_souboru):
    """Hlavní program, který stahuje a zpracovává data
    ze zadané URL adresy, který poté data vyexportuje do csv souboru."""
    data = scraper_dat(url)
    export_do_csv(data, nazev_vytupniho_csv_souboru)
    print(f"UKONČUJI PROGRAM ELECTION SCRAPER.")


# ########### EXPORT DO CSV ###########
def export_do_csv(data, vystupni_soubor):
    """Export získaných dat do CSV souboru."""
    print(f"UKLÁDÁM DATA DO SOUBORU: {vystupni_soubor}")
    # byl použit encoding="utf-8-sig" namísto "utf-8", při kterém se chybně zobrazovala diakritika při otevření v MS EXCEL
    with open(vystupni_soubor, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        fieldnames = data[0].keys()  # Získá názvy sloupců z klíčů slovníků
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)  # Zapíše všechny řádky
    print(f"PROGRAM ÚSPEŠNĚ VYTVOŘIL CSV SOUBOR.")





test_x = election_scraper(vstupni_url, vystupni_soubor)
# for udaj in test_x:
#     print(udaj)






