"""
election_scraper3.py: třetí projekt do Engeto Online Python Akademie

author: Marek Pošmura
email: m.posmuar@seznam.cz
"""

import requests
from bs4 import BeautifulSoup

# zharaničí dodělat, pokud zbude čas.
# pip freeze > requirements.txt - pro vytvoření souboru s knihovnami, na závěr projektu

# Práce s Gitem - základní postup pro odeslání změn na GitHub
# Při každé změně postupuj takto:

    # git add .                     # přidání všech změn 
    # git commit -m "Popis změny"   # commit změn s popisem
    # git push origin main          # odeslání změn na GitHub




# vstupní soubory
url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203" # URL adresa pro okres Náchod
vystupni_spubor = "vystup_nachod.csv"

# pokus

# https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5203
# musí se jít pře druhý křížek, kde je seznam obcí  


odp_serveru = requests.get(url)
# print(odp_serveru.text) # vypíše obsah stránky

soup = BeautifulSoup(odp_serveru.text, 'html.parser')

# print(soup.prettify()) # vypíše obsah stránky s odsazením

# print(soup.find_all("<a>")) # vypíše všechny odkazy na stránce


links = soup.find_all("a") # vypíše všechny odkazy na stránce. Výsledek je seznam, kde každý prvek je odkaz na stránce. 

# vypíše všechny odkazy na stránce. 
print("##########################################")
odkazy = []

base_url = "https://www.volby.cz/pls/ps2017nss/"

for link in links:
    
    href = base_url+link.get("href")  # Získáme URL z atributu href
    
    # Pokud je odkaz už v seznamu, nebo neobsahuje "vyber", přeskočíme ho.
    if href in odkazy or "vyber" not in href:
        continue
    
    # Pokud není, přidáme ho do seznamu
    odkazy.append(href) 



# print("\n".join(odkazy)) # kontrolní print
print(len(odkazy)) # kontrolní print



# vytvořit slovník okresů a čísel okresů....podle čísla se možná pujde lépe orientovat v URL adresách


