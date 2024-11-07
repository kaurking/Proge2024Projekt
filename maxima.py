import requests
import json
import pandas as pd
import urllib.parse
from tabulate import tabulate
from bs4 import BeautifulSoup
import re

sisend = str(input("Sisestage otsiv toode, nt piim: "))
encoded_sisend = urllib.parse.quote(sisend)  # URL encode the product name for safe usage in the query string

if sisend:
    page_num = 1
    maxima_tootenimed = []
    maxima_toote_hind = []
    
    while True:
        url = f'https://www.barbora.ee/otsing?q={encoded_sisend}&page={page_num}'
        
        page = requests.get(url)

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            
            # Leiame 'script' tag-i mis sisaldab json koodi.
            script_tag = soup.find('script', string=re.compile(r'window\.b_productList = \[.*\];'))
            
            if script_tag:
                # Eraldame JSON sõne
                json_tekst = re.search(r'window\.b_productList = (\[.*\]);', script_tag.string).group(1)
                # JSON sõne listi
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

        # Move to the next page
        page_num += 1

    # Create a dataframe with the scraped data
    maxima_list = {'Toode:': maxima_tootenimed, 'Hind:': maxima_toote_hind}
    df_maxima = pd.DataFrame(maxima_list)
    
    # Print the results in a table format
    print(tabulate(df_maxima, headers='keys', tablefmt='psql'))
