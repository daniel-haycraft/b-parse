import requests
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/properties/normalized_address"
property_url = "https://webapp.forecasa.com/api/v1/properties"

with open('Dead Deal Data Look Up Month.2025.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)

def fetch_properties(li):
    # Subtract 30 days from Application Date
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

    url_params = {
        "api_key": key,
        "page": 1,
        "address": addressv1,
    }
    property_params = {
        "api_key": key,
        "page": 1,
        "page_size": 1000,
        'q[last_mortgage_date_gteq]': date1_str,
        'q[last_mortgage_date_lteq]': date2_str,
        "search": addressv1,
    }

     try:
        response = requests.get(url_params, params=params, timeout=30)
        response.raise_for_status()
    except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
        print(f"Request issue for {li.get('Property Address', '<no address>')}: {e}")
        fallback = {**li}
        for k in ['fc_transaction_id', 'fc_house_id', 'FC Transaction Date', 'FC Maturity Date',
                  'FC Borrowing Entity', 'FC Lender', 'FC Loan Amount','FC MSA','FC Comp Amount','FC Lender Type','FC Company Id',
                  'Status','Loan Number','id','Property Address','city','state','zip','County','COE','CF1 Loan Amount',
                  'CF1 Loan Request','Purchase Price','UW Approved Amount','UW LA COE','uw_approved_amount_option_2','uw_approved_amount_option_2','LACOE Approved','Holdback','Holdback Approved','Relevant Metro','Cancellation Reason','Opt1 Purchase/Rehab','Opt2 Purchase/Rehab',
                  'Acquisition LTFV','Acquisition LTC','Acquisition LTCV','Acquisition LTPP','Rehab LTFV','Rehab LTC','Rehab LTCV',
                  'Rehab LTPP','PP Category','Canceled Reason W/ high leverage','Reason W/ high leverage on LTPP','Borrower Source','UW Approved Amount']:
            fallback.setdefault(k, '')
        fallback['recorded_date'] = ''
        fallback['Status'] = 'Not Found'
        return [fallback]

    normal_address = response.json().get('address', [])
    results = []