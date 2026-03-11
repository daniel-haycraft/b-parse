import requests
import csv
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import unicodedata
from rich.console import Console
from rich.syntax import Syntax
import json
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/properties"

# ---- speed / stability knobs (same API rules) ----
MAX_WORKERS = 10          # threads doing work
MAX_IN_FLIGHT = 6         # "not too fast" cap of simultaneous API calls
REQUEST_TIMEOUT = 30

DEBUG_PRETTY_PRINT = False  # set True only when debugging a few rows

# ---- thread-local session (safe under threads) + pooling ----
thread_local = threading.local()
api_sema = threading.Semaphore(MAX_IN_FLIGHT)

def get_session():
    s = getattr(thread_local, "session", None)
    if s is None:
        s = requests.Session()
        retry = Retry(
            total=2,
            backoff_factor=0.4,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=MAX_WORKERS,
            pool_maxsize=MAX_WORKERS,
        )
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        thread_local.session = s
    return s

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}

def pretty_print_dict(data):
    console = Console()
    formatted = json.dumps(data, indent=4, ensure_ascii=False)
    syntax = Syntax(formatted, "json", theme="monokai", line_numbers=False)
    console.print(syntax)

loadcsv = 'month'

# Load CSV
with open(f'Dead Deal Data Look Up {loadcsv}.2026.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)

# (kept exactly as you had it)
FALLBACK_KEYS = [
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
]

def fallback_row(li, status='Not Found'):
    fallback = {**li}
    for k in FALLBACK_KEYS:
        fallback.setdefault(k, '')
    fallback['recorded_date'] = ''
    fallback['Status'] = status
    return fallback

def fetch_transactions(li):
    # --- COE parse (prevents crashes) ---
    coe_str = (li.get("coe") or li.get("COE") or "").strip()
    try:
        date1 = datetime.strptime(coe_str, "%m/%d/%Y") - timedelta(days=30)
    except Exception:
        return [fallback_row(li, status="Bad COE")]

    date1_str = date1.strftime("%m/%d/%Y")
    date2_str = datetime.today().strftime("%m/%d/%Y")

    # --- address handling (fixes your always-true condition) ---
    addressv1 = (li.get("formatted_address") or "").strip()

    if not addressv1:
        addressv1 = f'{li.get("property_address","")}, {li.get("city","")}, {li.get("state","")} {li.get("zip","")}'.strip()

        # keep your unit normalization behavior
        if 'Unit' in addressv1:
            addressv1 = addressv1.replace(' Unit', ', Unit ').strip().title()

        if '#' in addressv1:
            addressv1 = addressv1.replace(' #', ', Unit ').strip().title()

        if 'apt' in addressv1:
            addressv1 = addressv1.replace(' apt', ', apt ').strip().title()

        if 'ste' in addressv1:
            addressv1 = addressv1.replace(' ste', ', ste ').strip().title()
    else:
        addressv1 = addressv1.strip().title()

    params = {
        "api_key": key,
        "page": 1,
        "page_size": 1,
        'q[last_mortgage_date_gteq]': date1_str,
        'q[last_mortgage_date_lteq]': date2_str,
        "search": addressv1,
    }

    # --- 429 handling + throttling (same “rules” as your other script) ---
    backoff = 2
    max_backoff = 20

    while True:
        try:
            with api_sema:
                response = get_session().get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 429:
                sleep_for = min(backoff, max_backoff) + random.uniform(0, 0.5)
                print(f"[{datetime.now()}] 429 hit → sleeping {sleep_for:.1f}s → {addressv1}", flush=True)
                time.sleep(sleep_for)
                backoff = min(backoff * 2, max_backoff)
                continue

            response.raise_for_status()
            break

        except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
            print(f"Request issue for properties.py {li.get('formatted_address', '<no address>')}: {e}", flush=True)
            return [fallback_row(li, status="Not Found")]

    data = safe_json(response)
    properties = data.get('properties', []) or []
    results = []

    for t in properties:
        merged = {**t, **li}
        if DEBUG_PRETTY_PRINT:
            pretty_print_dict(merged)
        merged["Status"] = "Found"
        results.append(merged)

    if not results:
        return [fallback_row(li, status="Not Found")]

    return results


# Run all requests in parallel (same behavior, but safer + progress)
data_array = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(fetch_transactions, li) for li in lister]
    total = len(futures)

    for i, future in enumerate(as_completed(futures), 1):
        data_array.extend(future.result() or [])
        if i % 25 == 0 or i == total:
            print(f"Progress: {i}/{total}", flush=True)

# Prepare CSV
csv_name = f'Report completed {loadcsv}.csv'

# Use pandas for speed
df = pd.DataFrame(data_array)

def safe_col(name):
    return df.get(name, pd.Series('', index=df.index))

# ---- df_out (UNCHANGED from your paste) ----
df_out = pd.DataFrame({
    'fc_transaction_id': safe_col('∩╗┐fc_transaction_id'),
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
    'opt_1_simplified': '=IF(ISTEXT(AH2), "",IF(AA2<-10000000,"-10M+",IF(AC2<-1000000,"-10m to -1m",IF(AC2<=-500000,"-1M to -500K",IF(AC2<=-200000,"-500K to -200K",IF(AC2<=-75000,"-200K to -75K",IF(AC2<=-50000,"-75K to -50K",IF(AC2<=-25000,"-50K to -25K",IF(AC2<=-10000,"-25K to -10K",IF(AC2<0,"-10K to 0",IF(AC2<=10000,"0–10K",IF(AC2<=25000,"10K–25K",IF(AC2<=50000,"25K–50K",IF(AC2<=75000,"50K–75K",IF(AC2<=200000,"75K–200K",IF(AC2<=500000,"200K–500K",IF(AC2<1000000,"500K–1M","1M+")))))))))))))))))',
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
    "Town": safe_col("town"),
    "transaction_count": safe_col("transactions_count"),
    "mtg1_loan_amt": safe_col("mtg1_loan_amt"),
    "mtg1_lender": safe_col("mtg1_lender"),
    "last_mortgage_date": safe_col("last_mortgage_date"),
    "last_mortgage_amount": safe_col("last_mortgage_amount"),
    "parcel_number": safe_col("parcel_number"),
    'formatted_address': safe_col('formatted_address'),
})

# Normalize strings in all columns
df_out = df_out.apply(lambda col: col.map(lambda x: unicodedata.normalize('NFKD', str(x)) if isinstance(x, str) else x))
df_out.to_csv(csv_name, index=False, encoding='utf-8-sig')