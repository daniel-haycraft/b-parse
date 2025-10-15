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

def fetch_transactions(li):
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

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
        print(f"Request issue for {li.get('Property Address', '<no address>')}: {e}")
        fallback = {**li}
        for k in ['fc_transaction_id', 'fc_house_id', 'FC Transaction Date', 'FC Maturity Date',
                  'FC Borrowing Entity', 'FC Lender', 'FC Loan Amount','FC MSA','FC Comp Amount','FC Lender Type','FC Company Id',
                  'Status','Loan Number','id','Property Address','city','state','zip','County','COE','CF1 Loan Amount',
                  'CF1 Loan Request','Purchase Price','UW Approved Amount','UW LA COE','LACOE Approved','Holdback','Holdback Approved','Relevant Metro','Cancellation Reason','Opt1 Purchase/Rehab','Opt2 Purchase/Rehab',
                  'Acquisition LTFV','Acquisition LTC','Acquisition LTCV','Acquisition LTPP','Rehab LTFV','Rehab LTC','Rehab LTCV',
                  'Rehab LTPP','PP Category','Canceled Reason W/ high leverage','Reason W/ high leverage on LTPP','Borrower Source','UW Approved Amount']:
            fallback.setdefault(k, '')
        fallback['recorded_date'] = ''
        fallback['Status'] = 'Not Found'
        return [fallback]

    transactions = response.json().get('transactions', [])
    results = []

    for t in transactions:
        merged = {**li, **t}

        # Extract lender type and company IDs
        lender_types = []
        company_ids = []
        meta = t.get("transaction_meta", {})
        for group in ["companies", "cross_companies"]:
            for comp in meta.get(group, []):
                lender_types.extend(comp.get("tags", []))
                if comp.get("id"):
                    company_ids.append(str(comp["id"]))

        merged["Lender Type"] = ", ".join(sorted(set(lender_types))) if lender_types else ""
        merged["Company Id"] = ", ".join(sorted(set(company_ids))) if company_ids else ""

        # Safe conversion of recorded_date
        rec = merged.get('recorded_date', '')
        if rec:
            try:
                merged["recorded_date"] = datetime.strptime(rec.replace("-", "/"), "%Y/%m/%d")
            except Exception:
                merged["recorded_date"] = rec

        merged["Status"] = "Found"
        results.append(merged)

    # Fallback row if no API results
    if not results:
        fallback = {**li}
        for k in ['fc_transaction_id', 'fc_house_id', 'FC Transaction Date', 'FC Maturity Date',
                  'FC Borrowing Entity', 'FC Lender', 'FC Loan Amount','FC MSA','FC Comp Amount','FC Lender Type','FC Company Id',
                  'Status','Loan Number','id','Property Address','city','state','zip','County','COE','CF1 Loan Amount',
                  'CF1 Loan Request','Purchase Price','UW Approved Amount','UW LA COE','LACOE Approved','Holdback','Holdback Approved','Relevant Metro','Cancellation Reason','Opt1 Purchase/Rehab','Opt2 Purchase/Rehab',
                  'Acquisition LTFV','Acquisition LTC','Acquisition LTCV','Acquisition LTPP','Rehab LTFV','Rehab LTC','Rehab LTCV',
                  'Rehab LTPP','PP Category','Canceled Reason W/ high leverage','Reason W/ high leverage on LTPP','Borrower Source','UW Approved Amount']:
            fallback.setdefault(k, '')
        fallback['recorded_date'] = ''
        fallback['Status'] = 'Not Found'
        return [fallback]

    return results

# Run all requests in parallel
data_array = []
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_li = {executor.submit(fetch_transactions, li): li for li in lister}
    for future in as_completed(future_to_li):
        data_array.extend(future.result() or [])

# Prepare CSV
csv_name = 'Dead Deal Data Look Up Month.2025.csv'

# Use pandas for speed
df = pd.DataFrame(data_array)

# Select & rename columns for CSV
df_out = pd.DataFrame({
    'fc_transaction_id': df.get('fc_transaction_id', ''),
    'fc_house_id': df.get('fc_house_id', ''),
    'FC Transaction Date': df.get('recorded_date', ''),
    'FC Maturity Date': df.get('mortgage_maturity_date', ''),
    'FC Borrowing Entity': df.get('grantor', ''),
    'FC Lender': df.get('grantee', ''),
    'FC Loan Amount': df.get('amount', ''),
    'County': df.get('county', ''),
    'FC MSA': df.get('msa_name', ''),
    'FC Comp Amount': df.get('amount', ''),
    'FC Lender Type': df.get('Lender Type', ''),  # ✅ renamed tags
    'FC Company Id': df.get('Company Id', ''),    # ✅ new field
    'Status': df.get('Status', ''),            # ✅ found/not found indicator
    'Loan Number': df.get('loan', ''),
    'id': df.get('id', ''),
    'Property Address': df.get('property_address',''),
    'city': df.get('city',''),
    'state': df.get('state',''),
    'zip': df.get('zip',''),
    'COE':df.get('coe',''),
    'CF1 Loan Amount': df.get('loan_amount', ''),
    'CF1 Loan Request':df.get('loan_request',''),
    'Purchase Price':df.get('purchase_price',''),
    'UW Approved Amount':df.get('uw_approved_amount',''),
    'UW LA COE':df.get('uw_la_coe',''),
    'LACOE Approved':df.get('lacoe_approved'),
    'Holdback':df.get('holdback'),
    'Holdback Approved': df.get('holdback_approved'),
    'Relevant Metro':df.get('Relevant Metro',''),
    'Cancellation Reason':df.get('Cancellation Reason',''),
    'Opt1 Purchase/Rehab':df.get('Opt1 Purchase/Rehab',''),
    'Opt2 Purchase/Rehab':df.get('Opt2 Purchase/Rehab',''),
    'Acquisition LTFV':df.get('Acquisition LTFV',''),
    'Acquisition LTC':df.get('Acquisition LTC',''),
    'Acquisition LTCV':df.get('Acquisition LTCV',''),
    'Acquisition LTPP':df.get('Acquisition LTPP',''),
    'Rehab LTFV':df.get('Rehab LTFV',''),
    'Rehab LTC':df.get('Rehab LTC',''),
    'Rehab LTCV':df.get('Rehab LTCV',''),
    'Rehab LTPP':df.get('Rehab LTPP',''),
    'PP Category':df.get('PP Category',''),
    'Canceled Reason W/ high leverage':df.get('Canceled Reason W/ high leverage',''),
    'Canceled Reason W/ high leverage on LTPP':df.get('Canceled Reason W/ high leverage on LTPP',''),
    'Borrower Source': df.get('Borrower Source','')
})

df_out.to_csv(csv_name, index=False)
