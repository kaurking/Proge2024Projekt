import requests
import jinja2
import json
import re
import pandas as pd
import urllib.parse
from tabulate import tabulate
from bs4 import BeautifulSoup

sisend = str(input("Sisestage otsiv toode, nt piim: "))
urllib.parse.quote(sisend)
if sisend:
    url = 'https://www.barbora.ee/otsing?q=' + sisend
    page = requests.get(url)

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        # Leiame 'script' tag-i mis sisaldab json koodi.
        script_tag = soup.find('script', string=re.compile(r'window\.b_productList = \[.*\];'))
        maxima_tootenimed = []
        maxima_toote_hind = []
        # Eraldame JSON andmed JavaScriptist
        if script_tag:
            # Eraldame JSON sõne
            json_tekst = re.search(r'window\.b_productList = (\[.*\]);', script_tag.string).group(1)

            # JSON sõne listi
            toote_list = json.loads(json_tekst)

            # Eraldame tootenimed ja hinnad
            for toode in toote_list:
                tootenimi = toode.get('title')
                hind = toode.get('price')
                maxima_tootenimed.append(tootenimi)
                maxima_toote_hind.append(hind)
    else:
        print("Barbora.ee (Maxima) ei ole hetkel saadaval.")

    # Laeme tooted ja hinnad tabelisse
    maxima_list = {'Toode:': maxima_tootenimed, 'Hind:': maxima_toote_hind}
    df_maxima = pd.DataFrame(maxima_list)
    print(tabulate(df_maxima, headers = 'keys', tablefmt = 'psql'))