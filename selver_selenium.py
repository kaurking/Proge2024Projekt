from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time

sisend = str(input("Sisestage otsiv toode, nt piim: "))

# Eemaldab mingisugused kahtlased non-essential errorid seotud mingi USB jamaga (võib ära võtta, siis kood töötab, aga mingid sõnumid tulevad)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

urllib.parse.quote(sisend)
url = 'https://www.selver.ee/search?q=' + sisend

driver.get(url)

try:

    for i in range(1):  # scrollib lihtsalt faili lõppu?
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # ootab, et laadida contenti


    # Selveri lehel on kõik tooded "Kaartidena" --> laeb kaardid
    tootekaart = WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductCard'))
    )

    tooted = []
    hinnad = []
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

    # print listid ja nende pikkused, kontrollisin info ühe näitega üle, peaks töötama kogu kood.
    print(len(tooted))
    print(len(hinnad))
    print(tooted)
    print(hinnad)

finally:
    driver.quit()