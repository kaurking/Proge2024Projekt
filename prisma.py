import time
import pandas as pd
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import urllib.parse

max_read = 20

app = Flask(__name__)

def prisma(sisend):
    # Eemaldab mingisugused kahtlased non-essential errorid seotud mingi USB jamaga (võib ära võtta, siis kood töötab, aga mingid sõnumid tulevad)
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
        time.sleep(2)
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

print(prisma("piim"))