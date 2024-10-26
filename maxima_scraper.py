from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://barbora.ee/otsing?q=hakkliha")

# Oota kuniks kõik elemendid laevad
wait = WebDriverWait(driver, 10)

# leia tootenimed
nimed = driver.find_elements(By.CSS_SELECTOR, "a.tw-break-words.tw-text-b-paragraph-sm.tw-text-neutral-900.tw-no-underline.tw-transition.tw-duration-100.tw-ease-out.hover\\:tw-text-red-600.active\\:tw-text-red-700.lg\\:tw-text-base")

tootenimed = []
# Lisa tootenimed listi 'tootenimed'
for nimi in nimed:
    tootenimi = nimi.find_element(By.TAG_NAME, "span").text
    tootenimed.append(tootenimi)

# Finding prices (with escaped square brackets)
hinna_blokk = driver.find_elements(By.CSS_SELECTOR, "div.tw-mb-\\[2px\\].tw-w-fit.tw-rounded-lg")

täishind = []
for blokk in hinna_blokk:
    try:
        hind_osa1 = blokk.find_element(By.CSS_SELECTOR, "span.tw-pr-\\[2px\\].tw-text-xl.tw-font-bold").text
        hind_osa2 = blokk.find_element(By.CSS_SELECTOR, "span.tw-pr-\\[1px\\].tw-text-sm.tw-font-bold").text
        valuuta = blokk.find_element(By.CSS_SELECTOR, "span.tw-text-sm.tw-leading-\\[15px\\]").text
        kokku = hind_osa1 + "." + hind_osa2 + " " + valuuta
        täishind.append(kokku)
    except Exception as e:
        print("Viga! Ei saanud hindu väljastada:", e)

print(len(tootenimed))
print(len(täishind))
print(tootenimed)
print(täishind)
driver.quit()
