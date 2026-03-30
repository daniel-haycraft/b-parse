import requests
import csv
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import unicodedata

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/properties/normalize_address"

# Load CSV
with open('Dead Deal Data.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)

csv_name = 'dead deal awaiting for transactions.csv'
data_array = []


def fetch_transactions(li):

    addressv1 =li["property_address"]

    if 'Unit' in addressv1:
        addressv1 = addressv1.replace(' Unit', ', Unit ').strip()

    if '#' in addressv1:
        addressv1 = addressv1.replace(' #', ', Unit ').strip()

    if 'apt' in addressv1:
        addressv1 = addressv1.replace(' apt', ', apt ').strip()

    if 'ste' in addressv1:
        addressv1 = addressv1.replace(' ste', ', ste ').strip()

    addressv1 = addressv1.strip().title()

    params = {
        "api_key": key,
        "address": addressv1,
    }

    # Retry forever on 429
    while True:

        try:

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:
                print(f"[{datetime.now()}] 429 → sleeping 10s → {addressv1}")
                time.sleep(10)
                continue

            response.raise_for_status()
            break

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.RequestException) as e:

            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                print(f"[{datetime.now()}] 429 exception → sleeping 10s → {addressv1}")
                time.sleep(10)
                continue

            # ORIGINAL FALLBACK (UNCHANGED)
            print(f"[{datetime.now()}] FALLBACK → {addressv1}")

            fallback = {**li}

            for k in [
                'Full Address','Loan Number','id','Property Address','city',
                'state','zip','COE','CF1 Loan Amount','CF1 Loan Request',
                'Purchase Price','Transaction Type','Total Cost',
                'UW Approved Amount option 1','UW LA COE Amount option 1',
                'Opt 1 Delta','Opt 1 Simplified','Opt 1 Percent',
                'uw_approved_amount_option_2','uw_la_coe_option_2',
                'Delta Opt 2','Opt 2 Simplified','Opt 2 Percent',
                'LACOE Approved','Holdback','Holdback Approved',
                'Relevant Metro','Cancellation Reason',
                'Opt1 Purchase/Rehab','Opt2 Purchase/Rehab',
                'Acquisition LTFV','Acquisition LTC','Acquisition LTCV',
                'Acquisition LTPP','Rehab LTFV','Rehab LTC','Rehab LTCV',
                'Rehab LTPP','PP Category',
                'Canceled Reason W/ high leverage',
                'Canceled Reason W/ high leverage on LTPP',
                'Borrower Source'
            ]:
                fallback.setdefault(k, '')

            fallback['recorded_date'] = ''
            fallback['Status'] = 'Not Found'

            return fallback

    # SUCCESS
    address = response.json()

    merged = {**address, **li}
    merged["Status"] = "Found"

    print(f"[{datetime.now()}] SUCCESS → {addressv1}")

    return merged


# Run executor
with ThreadPoolExecutor(max_workers=1) as executor:

    futures = [executor.submit(fetch_transactions, li) for li in lister]

    for i, future in enumerate(as_completed(futures), 1):

        result = future.result()

        data_array.append(result)

        print(f"Progress: {i}/{len(lister)}")

        # checkpoint write every 5 rows
        if i % 5 == 0:

            df_checkpoint = pd.DataFrame(data_array)

            df_checkpoint.to_csv(
                csv_name,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"Checkpoint saved → {i}")


# FINAL FULL OUTPUT (YOUR ORIGINAL STRUCTURE)
df = pd.DataFrame(data_array)


def safe_col(name):
    return df.get(name, pd.Series('', index=df.index))


df_out = pd.DataFrame({

    'Status': safe_col('Status'),
    'loan': safe_col('loan'),
    'id': safe_col('∩╗┐id'),
    'property_address': safe_col('property_address'),
    'city': safe_col('city'),
    'state': safe_col('state'),
    'zip': safe_col('zip'),
    'coe': safe_col('coe'),
    'loan_amount': safe_col('loan_amount'),
    'loan_request': safe_col('loan_request'),
    'purchase_price': safe_col('purchase_price'),
    'transaction_type': safe_col('transaction_type'),
    'total_cost': safe_col('total_cost'),
    'uw_approved_amount': safe_col('uw_approved_amount'),
    'uw_la_coe': safe_col('uw_la_coe'),

    'opt_1_delta': '=IF(ISBLANK($G2),"No Forecasa Data",IF($AP2="Acquisition",MAX($AA2,$AB2)-$G2,IF($AP2="Rehab",MAX($AA2,$AB2+AL2)-$G2,"No Terms Given")))',

    'opt_1_simplified': '=FORMULA',

    'opt_1_percent': '=IF(ISTEXT(AC2),"",MIN(AC2,$G2)/MAX(AC2,$G2))',

    'uw_approved_amount_option_2': safe_col('uw_approved_amount_option_2'),
    'uw_la_coe_option_2': safe_col('uw_la_coe_option_2'),

    'delta_opt_2': '=FORMULA',

    'opt_2_simplified': '=FORMULA',

    'opt_2_percent': '=IF(ISTEXT(AH2),"",MIN(AH2,$G2)/MAX(AH2,$G2))',

    'lacoe_approved': safe_col('lacoe_approved'),
    'holdback': safe_col('holdback'),
    'holdback_approved': safe_col('holdback_approved'),

    'Relevant Metro': safe_col('Relevant Metro'),
    'Cancellation Reason': safe_col('Cancellation Reason'),

    'Opt1 Purchase/Rehab': safe_col('Opt1 Purchase/Rehab'),
    'Opt2 Purchase/Rehab': safe_col('Opt2 Purchase/Rehab'),

    'Acquisition LTFV': safe_col('Acquisition LTFV'),
    'Acquisition LTC': safe_col('Acquisition LTC'),
    'Acquisition LTCV': safe_col('Acquisition LTCV'),
    'Acquisition LTPP': safe_col('Acquisition LTPP'),

    'Rehab LTFV': safe_col('Rehab LTFV'),
    'Rehab LTC': safe_col('Rehab LTC'),
    'Rehab LTCV': safe_col('Rehab LTCV'),
    'Rehab LTPP': safe_col('Rehab LTPP'),

    'PP Category': safe_col('PP Category'),

    'Canceled Reason W/ high leverage': safe_col('Canceled Reason W/ high leverage'),
    'Canceled Reason W/ high leverage on LTPP': safe_col('Canceled Reason W/ high leverage on LTPP'),

    'Borrower Source': safe_col('Borrower Source'),

    'formatted_address': safe_col('formatted_address'),

})


# Normalize unicode
df_out = df_out.apply(
    lambda col: col.map(
        lambda x: unicodedata.normalize('NFKD', str(x))
        if isinstance(x, str) else x
    )
)

df_out.to_csv(csv_name, index=False, encoding='utf-8-sig')

print("DONE — FULL CSV WRITTEN")



