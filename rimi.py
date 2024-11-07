import requests
import jinja2
import json
import re
import pandas as pd
import urllib.parse
from tabulate import tabulate
from bs4 import BeautifulSoup

sisend = str(input("Sisestage otsiv toode, nt piim: "))
encoded = urllib.parse.quote(sisend)

if sisend:
    page_num = 1
    baas_url = 'https://www.rimi.ee/epood/ee/otsing?currentPage={}&pageSize=20&query={}'.format(page_num, encoded)
    rimi_tootenimed = []
    rimi_toote_hinnad = []
    while True:
        url = baas_url.format(page_num)
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            rimi_elements = soup.find_all(attrs={'data-gtm-eec-product': True})
            for toote_info in rimi_elements:
                product_data = json.loads(toote_info['data-gtm-eec-product'])
                nimi = product_data.get('name')
                hind = product_data.get('price')
                rimi_tootenimed.append(nimi)
                rimi_toote_hinnad.append(hind)
        page_num += 1
        else:
            break

    # Laeme tooted ja hinnad tabelisse
    rimi_list = {'Toode:': rimi_tootenimed, 'Hind:': rimi_toote_hinnad}
    df_rimi = pd.DataFrame(rimi_list)
    print(tabulate(df_rimi, headers = 'keys', tablefmt = 'psql'))