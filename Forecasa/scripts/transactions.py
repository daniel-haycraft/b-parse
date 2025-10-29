import requests
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import unicodedata

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/transactions"
loadcsv='month'
# Load CSV
with open(f'dead deal awaiting for transactions.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)

def fetch_transactions(li):
    # Subtract 30 days from Application Date
    date1 = datetime.strptime(li["coe"], "%m/%d/%Y") - timedelta(days=30)
    date1_str = date1.strftime("%m/%d/%Y")
    date2_str = datetime.today().strftime("%m/%d/%Y")

    addressv1 = li.get("formatted_address") or ""
    if not addressv1.strip():
        addressv1 = f'{li["property_address"]}, {li["city"]}, {li["state"]} {li["zip"]}'

    # Normalize and clean address formatting
    replacements = {
        ' Unit': ', Unit ',
        ' #': ', Unit ',
        ' apt': ', apt ',
        ' ste': ', ste ',
    }
    for old, new in replacements.items():
        if old in addressv1:
            addressv1 = addressv1.replace(old, new)
    addressv1 = addressv1.strip().title()

    params = {
        "api_key": key,
        "page": 1,
        "page_size": 1,
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
        return [fallback_row(li, status='Not Found')]

    transactions = response.json().get('transactions', [])
    results = []

    for t in transactions:
        merged = {**t, **li}

        lender_types = []
        company_ids = []

        meta = t.get("transaction_meta", {})
        for group in ["companies", "cross_companies"]:
            for comp in meta.get(group, []):
                # ✅ Fixed: safely handle NoneType for tags
                lender_types.extend(comp.get("tags") or [])
                company_id = comp.get("company_id")
                if company_id:
                    company_ids.append(str(company_id))

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
        print(merged)

    if not results:
        return [fallback_row(li, status='Not Found')]

    return results

def fallback_row(li, status='Not Found'):
    fallback = {**li}
    for k in [
        'fc_transaction_id', 'fc_house_id', 'recorded_date', 'FC Maturity Date', 'FC Borrowing Entity', 'FC Lender',
        'FC Loan Amount', 'County', 'FC MSA', 'FC Comp Amount', 'FC Est Compt LTC', 'FC Lender Type',
        'FC Company Id', 'Status', 'Loan Number', 'id', 'Property Address', 'city',
        'state', 'zip', 'COE', 'CF1 Loan Amount', 'CF1 Loan Request', 'Purchase Price',
        'Transaction Type', 'Total Cost', 'UW Approved Amount option 1', 'UW LA COE Amount option 1', 'Opt 1 Delta', 'Opt 1 Simplified',
        'Opt 1 Percent', 'uw_approved_amount_option_2', 'uw_la_coe_option_2', 'Delta Opt 2', 'Opt 2 Simplified', 'Opt 2 Percent',
        'LACOE Approved', 'Holdback', 'Holdback Approved', 'Relevant Metro', 'Cancellation Reason', 'Opt1 Purchase/Rehab',
        'Opt2 Purchase/Rehab', 'Acquisition LTFV', 'Acquisition LTC', 'Acquisition LTCV', 'Acquisition LTPP', 'Rehab LTFV',
        'Rehab LTC', 'Rehab LTCV', 'Rehab LTPP', 'PP Category', 'Canceled Reason W/ high leverage', 'Canceled Reason W/ high leverage on LTPP',
        'Borrower Source'
    ]:
        fallback.setdefault(k, '')
    fallback['recorded_date'] = ''
    fallback['Status'] = status
    return fallback

# Run all requests in parallel
data_array = []
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_li = {executor.submit(fetch_transactions, li): li for li in lister}
    for future in as_completed(future_to_li):
        data_array.extend(future.result() or [])

# Prepare CSV
csv_name = f'Dead Deal Data Look Up {loadcsv}.2025.csv'

df = pd.DataFrame(data_array)

def safe_col(name):
    return df.get(name, pd.Series('', index=df.index))

df_out = pd.DataFrame({
    'fc_transaction_id': safe_col('fc_transaction_id'),
    'fc_house_id': safe_col('fc_house_id'),
    'recorded_date': safe_col('recorded_date'),
    'mortgage_maturity_date': safe_col('mortgage_maturity_date'),
    'grantor': safe_col('grantor'),
    'grantee': safe_col('grantee'),
    'amount': safe_col('amount'),
    'county': safe_col('county'),
    'msa_name': safe_col('msa_name'),
    'comp_amount': safe_col('amount'),
    'est_compt_ltc': '=IF(ISBLANK($G2), "",$G2/$Z2)',
    'Lender Type': safe_col('Lender Type'),
    'Company Id': safe_col('Company Id'),
    'Status': safe_col('Status'),
    'loan': safe_col('loan'),
    'id': safe_col('id'),
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
    'transaction_type': safe_col('transaction_type'),
    'uw_approved_amount': safe_col('uw_approved_amount'),
    'uw_la_coe': safe_col('uw_la_coe'),
    'opt_1_delta': '=IF(ISBLANK($G2), "No Forecasa Data",IF($AP2="Acquisition",MAX($AA2,$AB2)-$G2,IF($AP2="Rehab",MAX($AA2,$AB2+AL2)-$G2,"No Terms Given, Forecasa funded ")))',
    'opt_1_simplified': '==IF(ISTEXT(AH2), "",IF(AA2<-10000000,"-10M+",IF(AC2<-1000000,"-10m to -1m",IF(AC2<=-500000,"-1M to -500K",IF(AC2<=-200000,"-500K to -200K",IF(AC2<=-75000,"-200K to -75K",IF(AC2<=-50000,"-75K to -50K",IF(AC2<=-25000,"-50K to -25K",IF(AC2<=-10000,"-25K to -10K",IF(AC2<0,"-10K to 0",IF(AC2<=10000,"0–10K",IF(AC2<=25000,"10K–25K",IF(AC2<=50000,"25K–50K",IF(AC2<=75000,"50K–75K",IF(AC2<=200000,"75K–200K",IF(AC2<=500000,"200K–500K",IF(AC2<1000000,"500K–1M","1M+")))))))))))))))))',
    'opt_1_percent': '=IF(ISTEXT(AC2), "", MIN(AC2,$G2)/MAX(AC2,$G2))',
    'uw_approved_amount_option_2': safe_col('uw_approved_amount_option_2'),
    'uw_la_coe_option_2': safe_col('uw_la_coe_option_2'),
    'delta_opt_2': '=IF(ISBLANK($G2),"No Forecasa Data",IF($AP2="Acquisition",MAX($AF2,$AG2)-$G2,IF($AP2="Rehab",MAX($AF2,$AG2+$AL2)-$G2,"No Terms Given, Forecasa funded ")))',
    'opt_2_simplified': '=IF(ISTEXT(AH2), "",IF(AH2<-10000000,"-10M+",IF(AH2<-1000000, "-10m to -1m",IF(AH2<=-500000,"-1M to -500K",IF(AH2<=-200000,"-500K to -200K",IF(AH2<=-75000,"-200K to -75K",IF(AH2<=-50000,"-75K to -50K",IF(AH2<=-25000,"-50K to -25K",IF(AH2<=-10000,"-25K to -10K",IF(AH2<0,"-10K to 0",IF(AH2<=10000,"0–10K",IF(AH2<=25000,"10K–25K",IF(AH2<=50000,"25K–50K",IF(AH2<=75000,"50K–75K",IF(AH2<=200000,"75K–200K",IF(AH2<=500000,"200K–500K",IF(AH2<=1000000,"500K–1M","1M+")))))))))))))))))',
    'opt_2_percent': '=IF(ISTEXT(AH2), "", MIN(AH2,$G2)/MAX(AH2,$G2))',
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

# Normalize all strings to avoid encoding issues
df_out = df_out.apply(lambda col: col.map(lambda x: unicodedata.normalize('NFKD', str(x)) if isinstance(x, str) else x))
df_out.to_csv(csv_name, index=False, encoding='utf-8-sig')
