import requests
import csv
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import unicodedata
import os
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# API and URL
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/transactions"
loadcsv = 'month'

# Output file
csv_name = f'Dead Deal Data Look Up {loadcsv}.2026.csv'

# Load source CSV
with open('dead deal awaiting for transactions.csv', "r", encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    lister = list(my_dict)

# Resume support
completed_addresses = set()
if os.path.exists(csv_name):
    try:
        existing_df = pd.read_csv(csv_name, encoding="utf-8-sig")
        completed_addresses = set(existing_df.get("formatted_address", []))
        print(f"Resuming: {len(completed_addresses)} already completed")
    except:
        pass

data_array = []

# -------------------------
# FAST CALL SETUP (only)
# -------------------------
MAX_WORKERS = 12          # total worker threads
MAX_IN_FLIGHT = 6         # max simultaneous requests hitting the API (safety valve)
REQUEST_TIMEOUT = 30

thread_local = threading.local()
api_sema = threading.Semaphore(MAX_IN_FLIGHT)

def get_session():
    """One requests.Session per thread (thread-safe + connection pooling)."""
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
            pool_maxsize=MAX_WORKERS
        )
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        thread_local.session = s
    return s

# -------------------------
# your original functions
# -------------------------

def fetch_transactions(li):

    date1 = datetime.strptime(li["coe"], "%m/%d/%Y") - timedelta(days=30)
    date1_str = date1.strftime("%m/%d/%Y")

    # KEEP YOUR ORIGINAL behavior (today), unless you decide to narrow it later.
    # Narrowing can massively speed up searches, but I'm not changing your logic here.
    date2_str = datetime.today().strftime("%m/%d/%Y")

    addressv1 = li.get("formatted_address") or ""
    if not addressv1.strip():
        addressv1 = f'{li["property_address"]}, {li["city"]}, {li["state"]} {li["zip"]}'

    replacements = {
        ' Unit': ', Unit ',
        ' #': ', Unit ',
        ' apt': ', apt ',
        ' ste': ', ste ',
    }

    for old, new in replacements.items():
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

    # Retry loop ONLY for 429 (kept), but made safer/faster
    backoff = 2
    max_backoff = 20

    while True:
        try:
            # throttle concurrent API calls
            with api_sema:
                response = get_session().get(url, params=params, timeout=REQUEST_TIMEOUT)

            # less noisy than printing the Response object every time
            # print(response)

            if response.status_code == 429:
                # small jitter prevents threads from retrying in sync
                sleep_for = backoff + random.uniform(0, 0.5)
                print(f"[{datetime.now()}] 429 hit → sleeping {sleep_for:.1f}s → {addressv1}")
                time.sleep(sleep_for)
                backoff = min(backoff * 2, max_backoff)
                continue

            response.raise_for_status()
            break

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.RequestException) as e:

            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                sleep_for = backoff + random.uniform(0, 0.5)
                print(f"[{datetime.now()}] 429 exception → sleeping {sleep_for:.1f}s → {addressv1}")
                time.sleep(sleep_for)
                backoff = min(backoff * 2, max_backoff)
                continue

            print(f"[{datetime.now()}] FALLBACK → {addressv1}")
            return fallback_row(li, status='Not Found')

    transactions = response.json().get('transactions', [])

    results = []

    for t in transactions:

        merged = {**t, **li}

        lender_types = []
        company_ids = []

        meta = t.get("transaction_meta", {})

        for group in ["companies", "cross_companies"]:
            for comp in meta.get(group, []):
                lender_types.extend(comp.get("tags") or [])
                cid = comp.get("company_id")
                if cid:
                    company_ids.append(str(cid))

        merged["Lender Type"] = ", ".join(sorted(set(lender_types)))
        merged["Company Id"] = ", ".join(sorted(set(company_ids)))

        rec = merged.get('recorded_date', '')
        if rec:
            try:
                merged["recorded_date"] = datetime.strptime(rec.replace("-", "/"), "%Y/%m/%d")
            except:
                pass

        merged["Status"] = "Found"

        print(f"[{datetime.now()}] SUCCESS → {addressv1}")

        results.append(merged)

    if not results:
        return [fallback_row(li, status='Not Found')]

    return results


def fallback_row(li, status='Not Found'):

    fallback = {**li}

    for k in [
        'fc_transaction_id','fc_house_id','recorded_date',
        'mortgage_maturity_date','fc_party_company',
        'fc_cross_party_company','amount','county','msa_name',
        'Lender Type','Company Id','Status'
    ]:
        fallback.setdefault(k, '')

    fallback['Status'] = status

    return fallback


# Executor with checkpoint writing + resume skip
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = []

    for li in lister:

        addr = li.get("formatted_address", "")

        if addr in completed_addresses:
            continue

        futures.append(executor.submit(fetch_transactions, li))

    total = len(futures)

    for i, future in enumerate(as_completed(futures), 1):

        result = future.result()

        if isinstance(result, list):
            data_array.extend(result)
        else:
            data_array.append(result)

        print(f"Progress: {i}/{total}")

        # checkpoint every 10 rows (kept exactly)
        if i % 10 == 0:

            df_checkpoint = pd.DataFrame(data_array)

            df_checkpoint.to_csv(
                csv_name,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"Checkpoint saved → {i}")


# Final dataframe build
df = pd.DataFrame(data_array)


def safe_col(name):
    return df.get(name, pd.Series('', index=df.index))


# -------------------------
# df_out: UNCHANGED
# -------------------------
df_out = pd.DataFrame({

    'fc_transaction_id': safe_col('fc_transaction_id'),
    'fc_house_id': safe_col('fc_house_id'),
    'recorded_date': safe_col('recorded_date'),
    'mortgage_maturity_date': safe_col('mortgage_maturity_date'),
    'grantor': safe_col('fc_party_company'),
    'grantee': safe_col('fc_cross_party_company'),
    'amount': safe_col('amount'),
    'county': safe_col('county'),
    'msa_name': safe_col('msa_name'),
    'comp_amount': safe_col('amount'),

    'est_compt_ltc': '=IF(ISBLANK($G2),"",$G2/$Z2)',

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

    'uw_approved_amount': safe_col('uw_approved_amount'),
    'uw_la_coe': safe_col('uw_la_coe'),

    'opt_1_delta': '=IF(ISBLANK($G2),"No Forecasa Data",IF($AP2="Acquisition",MAX($AA2,$AB2)-$G2,IF($AP2="Rehab",MAX($AA2,$AB2+AL2)-$G2,"No Terms Given")))',

    'opt_1_simplified': safe_col('opt_1_simplified'),
    'opt_1_percent': safe_col('opt_1_percent'),

    'uw_approved_amount_option_2': safe_col('uw_approved_amount_option_2'),
    'uw_la_coe_option_2': safe_col('uw_la_coe_option_2'),

    'delta_opt_2': safe_col('delta_opt_2'),
    'opt_2_simplified': safe_col('opt_2_simplified'),
    'opt_2_percent': safe_col('opt_2_percent'),

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


df_out = df_out.apply(
    lambda col: col.map(
        lambda x: unicodedata.normalize('NFKD', str(x))
        if isinstance(x, str) else x
    )
)

df_out.to_csv(csv_name, index=False, encoding='utf-8-sig')

print("DONE — FULL CSV WRITTEN")
