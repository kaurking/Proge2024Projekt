from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://barbora.ee/otsing?q=kodune")

nimi = driver.find_elements(By.CSS_SELECTOR, "a.tw-break-words.tw-text-b-paragraph-sm.tw-text-neutral-900.tw-no-underline.tw-transition.tw-duration-100.tw-ease-out.hover\\:tw-text-red-600.active\\:tw-text-red-700.lg\\:tw-text-base")

for nimed in nimi:
    span = nimed.find_element(By.TAG_NAME, "span")
    print(span.text)



driver.quit()