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

app = Flask(__name__)

def selver(sisend):
    # Eemaldab mingisugused kahtlased non-essential errorid seotud mingi USB jamaga (võib ära võtta, siis kood töötab, aga mingid sõnumid tulevad)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

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

    return pd.DataFrame({'Toode': tooted, 'Hind': hinnad})

def maxima(sisend):
    if sisend:
        page_num = 1
        maxima_tootenimed = []
        maxima_toote_hind = []

        while True:
            url = f'https://www.barbora.ee/otsing?q={sisend}&page={page_num}'
            page = requests.get(url)

            if page.status_code == 200:
                soup = BeautifulSoup(page.text, 'html.parser')
                # Leiame 'script' tag-i mis sisaldab json koodi.
                script_tag = soup.find('script', string=re.compile(r'window\.b_productList = \[.*\];'))

                if script_tag:
                    # Eraldame JSON sõne
                    json_tekst = re.search(r'window\.b_productList = (\[.*\]);', script_tag.string).group(1)
                    # JSON sõne listis
                    toote_list = json.loads(json_tekst)
                    
                    # Kui tooteid pole annab alla
                    if not toote_list:
                        break
                    
                    # Eraldame tootenimed ja hinnad
                    for toode in toote_list:
                        tootenimi = toode.get('title')
                        hind = toode.get('price')
                        maxima_tootenimed.append(tootenimi)
                        maxima_toote_hind.append(hind)
                else:
                    break
            else:
                break
            
            # Järgmine leht
            page_num += 1
        # Loob andmeraami
        return pd.DataFrame({'Toode': maxima_tootenimed, 'Hind': maxima_toote_hind})

def rimi(sisend):
    if sisend:
        url = 'https://www.rimi.ee/epood/ee/otsing?query=' + sisend
        page = requests.get(url)
        rimi_tootenimed = []
        rimi_toote_hinnad = []

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            rimi_elements = soup.find_all(attrs={'data-gtm-eec-product': True})
            for toote_info in rimi_elements:
                product_data = json.loads(toote_info['data-gtm-eec-product'])
                nimi = product_data.get('name')
                hind = product_data.get('price')
                rimi_tootenimed.append(nimi)
                rimi_toote_hinnad.append(hind)
        # Laeme tooted ja hinnad tabelisse
        return pd.DataFrame({'Toode': rimi_tootenimed, 'Hind': rimi_toote_hinnad})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    sisend = request.json.get('query')
    if not sisend:
        return jsonify({"error": "Palun sisesta toode!"}), 400

    # Fetch data
    selver_data = selver(sisend)
    maxima_data = maxima(sisend)
    rimi_data = rimi(sisend)

    data = {
        "Selver": selver_data.to_dict(orient='records'),
        "Maxima": maxima_data.to_dict(orient='records'),
        "Rimi": rimi_data.to_dict(orient='records')
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
