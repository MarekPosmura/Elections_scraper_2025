"""
election_scraper3.py: třetí projekt do Engeto Online Python Akademie

author: Marek Pošmura
email: m.posmuar@seznam.cz
"""

import requests
from bs4 import BeautifulSoup
import csv

line = 30 * "-"
line2 = 30 * "#"
# zharaničí dodělat, pokud zbude čas.
# pip freeze > requirements.txt - pro vytvoření souboru s knihovnami, na závěr projektu

# Práce s Gitem - základní postup pro odeslání změn na GitHub
# Při každé změně postupuj takto:

    # git add .                     # přidání všech změn
    # git commit -m "Popis změny"   # commit změn s popisem
    # git push origin main          # odeslání změn na GitHub

# print(odp_serveru.text) # vypíše obsah stránky
# print(soup.prettify()) # vypíše obsah stránky s odsazením
# print(soup.find_all("<a>")) # vypíše všechny odkazy na stránce


########## VSTUPNÍ PARAMETRY ##########
vstupni_url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203" # URL adresa pro okres Náchod 5203 - 78 obcí
vystupni_soubor = "vystup_nachod.csv"

print("##################ZAČÁTEK PROGRAMU########################")

def stahnout_odkazy_url(url): # vypíše všechny relevantní odkazy na stránce. Výsledek je seznam, kde každý prvek je odkaz na stránku.
  odp_serveru = requests.get(url)
  soup = BeautifulSoup(odp_serveru.text, 'html.parser')
  links = soup.find_all("a")

  platne_odkazy = []
  for link in links:
    href = link.get("href")  # Získání URL odkazu
    if href in platne_odkazy or "ps311" not in href:
      continue
    else:
      platne_odkazy.append(href)

  return upravit_absolutni_cestu_odkazu(platne_odkazy)

def upravit_absolutni_cestu_odkazu(links): # z relativní cesty odkazů získáme absolutní cesty - hlavně pro debugging
  base_url = "https://www.volby.cz/pls/ps2017nss/"
  absolutni_url = []

  for link in links:
    full_url = base_url + link
    absolutni_url.append(full_url)  # Přidáme odkazy s absolutni cestou

  return absolutni_url


# ###### KONTROLNÍ VYTSIKNUTÍ VŠECH ODKAZŮ NA STRÁNCE OKRESU ######
# odkazy = stahnout_odkazy_url(vstupni_url)
# print("\n".join(odkazy))
# print(f"Počet obcí v okrese: {len(odkazy)}")


def uloz_tabulku_na_strance(odkaz_obce, cislo_tabulky): # uloží veškeré tabulky na stránce na seznam <class 'bs4.element.ResultSet'>
  odp_serveru = requests.get(odkaz_obce)
  soup = BeautifulSoup(odp_serveru.text, 'html.parser')
  tabulky = soup.find_all("table") # Najde všechny tabulky na stránce

  if len(tabulky) < cislo_tabulky:
      print(f"Chyba: Na stránce není {cislo_tabulky}. tabulka, nalezeno pouze {len(tabulky)} tabulek.")
      return None

  return tabulky[cislo_tabulky-1]



# ###### KONTROLNÍ VYTSIKNUTÍ SOUHRNNÉ TABULKY OBCE - ADRŠPACH ######
tabulka_x = uloz_tabulku_na_strance("https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=8&xobec=547786&xvyber=5203", 1)
print(line)
print(tabulka_x)
print(line)

def uloz_souhrnne_udaje_z_tabulky(souhrnna_tabulka): # uloží potřebné údaje ze souhrnné tebulky obce - výsledek je neupravený seznam buněk
  if souhrnna_tabulka is None:
    print("Chyba: Žádná tabulka nebyla nalezena.")
    return None
  else:
    vsechny_tr = souhrnna_tabulka.find_all("tr")
    tr = vsechny_tr[2] # požadovaný řádek
  return tr.find_all("td")  # Vrátíme seznam buněk

# print(line)
# print((uloz_souhrnne_udaje_z_tabulky(tabulka_x)))
# print(line)

def vyber_souhrnne_udaje_obce(td_bunky):
  if td_bunky is None or len(td_bunky) < 9:
    print("Chyba: Tabulka nemá dostatek buněk.")
    return None

  return {
    "volebni_ucast_%": td_bunky[5].getText().replace("\xa0", ""),
    "volici_v_seznamu": int(td_bunky[3].getText().replace("\xa0", "")),
    "vydane_obalky": int(td_bunky[4].getText().replace("\xa0", "")),
    "odevzdane_obalky": int(td_bunky[6].getText().replace("\xa0", "")),
    "platne_hlasy": int(td_bunky[7].getText().replace("\xa0", "")),
    "platne_hlasy_%": td_bunky[8].getText().replace("\xa0", "")
  }

def uloz_udaje_z_odkazu(odkazy):
  seznam_udaju = []
  pocet_odkazu = 10 # debugging
  for obec in odkazy:
    td_bunky = najdi_tabulku(obec)
    if td_bunky:
      seznam_udaju.append(vyber_souhrnne_udaje_obce(td_bunky))
      pocet_odkazu -= 1
      if pocet_odkazu == 0: # debugging
        break
    else:
      print("Nebyla nalezena žádná data.")

  return seznam_udaju

# ###### KONTROLNÍ VYTSIKNUTÍ ÚDAJŮ ZE SOUHRNNÉ TABULKY ######

odkazy = stahnout_odkazy_url(vstupni_url) # stáhne odkazy a upraví na absolutní cestu - výsledkem je seznam obcí (odkazů)
for obec in odkazy:
  tabulka = uloz_tabulku_na_strance(obec, 1)
  souhrnne_udaje_obce = uloz_souhrnne_udaje_z_tabulky(tabulka)





# ################## SAMOTNÝ PRŮBEH KODU ##################


# odkazy_obci = upravit_odkazy_na_seznam(stahnout_odkazy_url(vstupni_url))
# seznam_udaju_obce = uloz_udaje_z_odkazu(odkazy_obci) # seznam ve kterém se nachází souhrnné údaje o každé obci

# for udaj in seznam_udaju_obce: # debugging
#   print(udaj)


# stáhnutí údajů o jendotlivých politických stranách z obce



























# if t_table is None:
#     print(f"Tabulka nenalezena na stránce {obec}")
#     continue

# vsechny_tr = t_table.find_all("tr")
# if len(vsechny_tr) < 3:
#     print(f"Tabulka v {obec} má méně než 3 řádky")
#     continue

# tr = vsechny_tr[2] # požadovaný řádek
# return tr.find_all("td")  # Vrátíme seznam buněk








# def
# for odkaz_obce in odkazy_okres:
#     odp_serveru = requests.get(odkaz_obce)
#     soup = BeautifulSoup(odp_serveru.text, 'html.parser')
#     t_table = soup.find("table", {"class": "table"})
#     vsechny_tr = t_table.find_all("tr")
#     tr = vsechny_tr[2]
#     return


# #print(odp_serveru.text) # vypíše obsah stránky
# #print(soup.prettify()) # vypíše obsah stránky s odsazením
# #print(soup.find_all("<a>")) # vypíše všechny odkazy na stránce

# # vypíše údaje z tabulky celkových výsledků obce
# t_table = soup2.find("table", {"class": "table"})
# # print(t_table.prettify()) # vypíše obsah stránky s odsazením
# # z vysledky_obec vyscrapovat potřebné údaje
# vsechny_tr = t_table.find_all("tr")

# tr = vsechny_tr[2]

# td_bunky = tr.find_all("td")  # Najdeme všechny <td> buňky
# # hodnoty = [td.get_text() for td in td_bunky]  # Extrahujeme text z každé buňky - asi nebudu potřebovat










