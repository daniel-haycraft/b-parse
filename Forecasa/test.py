import requests
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/transactions"

# Load CSV
with open('Dead Deal Data.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)
for li in lister:    
    date1 = datetime.strptime(li["coe"], "%m/%d/%Y") - timedelta(days=30)
    date2 = datetime.strptime(li["coe"], "%m/%d/%Y") + timedelta(days=60)
    date1_str = date1.strftime("%m/%d/%Y")
    date2_str = date2.strftime("%m/%d/%Y")
    addressv1 = f'{li["property_address"]}, {li["city"]}, {li["state"]} {li["zip"]}'
    if 'Unit' in addressv1:
        addressv1 = addressv1.replace(' Unit', ', Unit ').strip()
        print(addressv1)
    if '#' in addressv1:
        addressv1 = addressv1.replace(' #', ', Unit ').strip()
        print(addressv1)
    if 'apt' in addressv1:
        addressv1 = addressv1.replace(' apt', ', apt ').strip()
        print(addressv1)
    if 'ste' in addressv1:
        addressv1 = addressv1.replace(' ste', ', ste ').strip()
        print(addressv1)
    print(addressv1)
    addressv1 = addressv1.strip().title()
    params = {
        "api_key": key,
        "page": 1,
        "page_size": 1000,
        'q[transaction_date_gteq]': date1_str,
        'q[transaction_date_lteq]': date2_str,
        "q[transaction_type_in][]": "MORTGAGE",
        "q[property_address_cont]": addressv1,
        "q[state_code_in][]": li["state"]
    }
    response = requests.get(url, params=params)
    print('{')
    print(response.reason)
    print(response.status_code)
    print(response.text)
    print('}')
