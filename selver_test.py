from flask import Flask, render_template, request, jsonify
import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    previous_count = 0  # Keep track of scroll position

    try:
        time.sleep(2)
        while len(tooted) <= max_read:
            # Scroll to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow time for content to load

            # Locate all product cards
            tootekaart = driver.find_elements(By.CLASS_NAME, 'ProductCard')
            
            # Stop scrolling if no new products load
            if len(tootekaart) == previous_count:
                time.sleep(1)
                break  # No new items loaded
            previous_count = len(tootekaart)

        for el in tootekaart:
            if len(tooted) >= max_read:
                break 

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

print(selver("kohuke"))