import requests
import json
import pprint
import csv
import os
from datetime import datetime as dt
pp = pprint.PrettyPrinter(0)
key = "IBFP-FDUlIyAnY_mJuzIjg"
try:
    date1 = str(input("date1 like 01/01/0000 "))
except:
    date1 = str(input("date1 like 01/01/0000 "))
try:
    date2 = str(input("date2 like 01/01/0000 "))
except:
    date2 = str(input("date2 like 01/01/0000 "))

url = "https://webapp.forecasa.com/api/v1/transactions"
params={
"api_key": 'IBFP-FDUlIyAnY_mJuzIjg',
"page_size":25000,
'q[transaction_date_gteq]': date1,
"q[transaction_type_in][]":"MORTGAGE",
"q[company_tags_in][]":"private_lender",
'q[transaction_date_lteq]': date2,
'q[state_code_in][]':'CO',
}

data_array =[]
response = requests.get(url,params=params)
# Process the response data (assuming it's JSON)
data = response.json()
# pp.pprint(data)
transactions = data["transactions"]
for t in transactions:
    data_array.append(t)

row = 0
contactdate1=date1.replace("/",".")
contactdate2=date2.replace("/",".")
csv_name= f'CO {contactdate1} - {contactdate2}.csv'
with open(csv_name, 'w', newline='\n')as file:
    fieldnames = ['fc_transaction_id', 'Scrape LLC','Secondary LLC', 'Lender', 'state', 'county', 'msa', 'recorded date', 'updated at','days updated apart']
    wright = csv.DictWriter(file, fieldnames=fieldnames)
    wright.writeheader()
    for data in data_array:
        borrower = ''
    # print('Data')
    # pp.pprint(data)
    # print('Companies')
    # pp.pprint(companies)
        companies = data['transaction_meta']['companies']
        if companies is not None:
            for comps in companies:
                # print("comp!")
                # print(comps)
                if 'tags' not in comps or comps == None:
                    borrower=''
                    continue
                elif comps['tags']==None:
                    borrower = ''
                    continue
                elif 'tags' in comps:
                    if 'loan_buyer' not in comps['tags'] and 'private_lender_borrower' in comps['tags'] and 'borrower' in comps['tags']:
                        borrower=comps['party_name']
                        continue
                    elif 'private_lender' in comps['tags'] or 'loan_buyer' in comps['tags']:
                        lender = comps['party_name']
                        continue
                    else:
                        borrower = ''
                        continue
                else:
                    borrower=''

        recorded_date = data["recorded_date"].replace('-', '/')

        updated =data['fc_updated_at'].replace('-', '/')
        updated= updated.split('T')
        updated=updated[0]

        recorded_date = dt.strptime(recorded_date, "%Y/%m/%d")
        updated = dt.strptime(updated, "%Y/%m/%d")

        days = updated-recorded_date

        days=str(days)
        days=days.split(" ")
        days = int(days[0])
        wright.writerow({
        "fc_transaction_id": data['fc_transaction_id'],
        "Scrape LLC": data['grantor'],
        "Secondary LLC": borrower,
        "Lender": data["grantee"],
        "state": data["state_name"],
        "county": data["county"],
        "msa": data["msa_name"],
        "recorded date": str(recorded_date),
        "updated at": str(updated),
        "days updated apart": str(days)
        })
