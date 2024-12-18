################################################
# Programmeerimine I
# 2024/2025 sügissemester
#
# Projekt
# Teema: Toote Hinna Otsingu Programm
#
#
# Autorid: Jan Alar Alesmaa, Kaur Kingsepp
#
# mõningane eeskuju: Hinnavaatlus.ee
#
# Lisakommentaar (nt käivitusjuhend): Vajab chromedriver.exe. Käivitusjuhend on readme.md failis
#
##################################################

from flask import Flask, render_template, request, jsonify
import requests
import json
import re
import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tabulate import tabulate

# Pandas andmeraamistiku suurim ridade arv
max_read = 20

app = Flask(__name__)

def selver(sisend):
    # Eemaldab mingisugused kahtlased non-essential errorid seotud mingi USB jamaga (võib ära võtta, siis kood töötab, aga mingid sõnumid tulevad)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # driver setup
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    # Veebileht URL
    urllib.parse.quote(sisend)
    url = 'https://www.selver.ee/search?q=' + sisend

    driver.get(url)

    tooted = []
    hinnad = []

    try:
        for i in range(1):  # scrollib lihtsalt faili lõppu?
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # ootab, et laadida contenti
        
        # Selveri lehel on kõik tooded "Kaartidena" --> laeb kaardid
        tootekaart = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductCard'))
        )

        for el in tootekaart:
            # Leiab Tootenime kaardist
            nimeelement = el.find_elements(By.CLASS_NAME, 'ProductCard__link')
            target_index = 1  # spetsiifiline <a> järjestus HTML-is
            if len(nimeelement) > target_index:
                tootenimi = nimeelement[target_index].text
            else:
                tootenimi = None 
            
            # Paneb listi
            tooted.append(tootenimi)
            
            # Leiab Tootehinna kaardist
            hinnaelement = el.find_element(By.CLASS_NAME, 'ProductPrice')
            tootehind = hinnaelement.text.split("\n")[0]

            # Paneb listi
            hinnad.append(tootehind)

    finally:
        driver.quit()

    return pd.DataFrame({'Toode': tooted[:max_read], 'Hind': hinnad[:max_read]})

def prisma(sisend):

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # driver setup
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    
    # veebileht URL
    urllib.parse.quote(sisend)
    url = 'https://www.prismamarket.ee/' + 'products/search/' + sisend

    driver.get(url)

    # listid toodete jaoks
    tooted = []
    hinnad = []

    try:
        for i in range(1):  # scrollib lihtsalt faili lõppu?
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # ootab, et laadida contenti
        
        # Prisma lehel on kõik tooded "Kaartidena". 
        tootekaart = driver.find_elements(By.CLASS_NAME, "js-shelf-item")

        for el in tootekaart:
            # Leiab Tootenime kaardist
            nimeelement = el.find_element(By.CLASS_NAME, 'name')
            tootenimi = nimeelement.text.strip()
 
            # Paneb listi
            tooted.append(tootenimi)
            
            # Leiab Tootehinna esimese osa kaardist
            hinnaelement = el.find_element(By.CLASS_NAME, 'whole-number ')
            tootehind1 = hinnaelement.text.strip()

            # Leiab Tootehinna teise osa kaardist
            hinnaelement = el.find_element(By.CLASS_NAME, 'decimal')
            tootehind2 = hinnaelement.text.strip()

            tootehind = f"{tootehind1}.{tootehind2}"

            # Paneb listi
            hinnad.append(tootehind)

    finally:
        driver.quit()

    return pd.DataFrame({'Toode': tooted[:max_read], 'Hind': hinnad[:max_read]})

def maxima(sisend):
    # Kontrollime, kas sisend on olemas
    if sisend:
        page_num = 1
        maxima_tootenimed = []  # List toodete nimede jaoks
        maxima_toote_hind = []  # List toodete hindade jaoks

        while True:
            # Koostame URL-i päringu jaoks
            url = f'https://www.barbora.ee/otsing?q={sisend}&page={page_num}'
            page = requests.get(url)

            if page.status_code == 200:  # Kontrollime, kas päring oli edukas
                soup = BeautifulSoup(page.text, 'html.parser')
                # Leiame <script>-tagi, mis sisaldab toodete JSON andmeid
                script_tag = soup.find('script', string=re.compile(r'window\.b_productList = \[.*\];'))

                if script_tag:
                    # Eemaldame JSON andmed stringist
                    json_tekst = re.search(r'window\.b_productList = (\[.*\]);', script_tag.string).group(1)
                    # Parsime JSON stringi listiks
                    toote_list = json.loads(json_tekst)
                    
                    # Kui tooteid ei leidu, lõpetame tsükli
                    if not toote_list:
                        break
                    
                    # Lisame tootenimed ja hinnad vastavatesse listidesse
                    for toode in toote_list:
                        tootenimi = toode.get('title')
                        hind = toode.get('price')
                        maxima_tootenimed.append(tootenimi)
                        maxima_toote_hind.append(hind)
                else:
                    # Kui <script>-tagi ei leita, lõpetame tsükli
                    break
            else:
                # Kui päring ei olnud edukas, lõpetame tsükli
                break
            
            # Suurendame leheküljenumbrit järgmise lehe pärimiseks
            page_num += 1
        # Tagastame tooted ja hinnad Pandas andmeraamina
        return pd.DataFrame({'Toode': maxima_tootenimed[:max_read], 'Hind': maxima_toote_hind[:max_read]})

def rimi(sisend):
    # Kontrollib, kas sisend on olemas
    if sisend:
        url = 'https://www.rimi.ee/epood/ee/otsing?query=' + sisend
        page = requests.get(url)
        rimi_tootenimed = []  # List toodete nimede jaoks
        rimi_toote_hinnad = []  # List toodete hindade jaoks

        if page.status_code == 200:  # Kontrollib, kas päring oli edukas
            soup = BeautifulSoup(page.text, 'html.parser')
            # Otsime elemendid, millel on atribuut `data-gtm-eec-product`
            rimi_elements = soup.find_all(attrs={'data-gtm-eec-product': True})
            for toote_info in rimi_elements:
                # Laeme JSON andmed elemendist
                product_data = json.loads(toote_info['data-gtm-eec-product'])
                nimi = product_data.get('name')  # Toote nimi
                hind = product_data.get('price')  # Toote hind
                rimi_tootenimed.append(nimi)
                rimi_toote_hinnad.append(hind)
        # Tagastame tooted ja hinnad Pandas andmeraamina
        return pd.DataFrame({'Toode': rimi_tootenimed[:max_read], 'Hind': rimi_toote_hinnad[:max_read]})

@app.route('/')
def index():
    # Renderdame index.html
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Saame kasutaja sisendi JSON vormingus
    sisend = request.json.get('query')
    if not sisend:
        # Tagastame veateate, kui sisend puudub
        return jsonify({"error": "Palun sisesta toode!"}), 400

    # Pärime andmeid erinevatest kauplustest
    selver_data = selver(sisend)  # Selveri andmed
    maxima_data = maxima(sisend)  # Maxima andmed
    rimi_data = rimi(sisend)  # Rimi andmed
    
    

    # Koondame andmed ühte struktuuri
    data = {
        "Selver": selver_data.to_dict(orient='records'),
        "Maxima": maxima_data.to_dict(orient='records'),
        "Rimi": rimi_data.to_dict(orient='records')
    }
    
    # Tagastame andmed JSON vormingus
    return jsonify(data)

if __name__ == '__main__':
    # Käivitame rakenduse arendusrežiimis
    app.run(debug=True)
