import requests
import json
import pprint
import csv
import os
from datetime import datetime as dt
pp = pprint.PrettyPrinter(5)
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/transactions"
try:
    date1 = str(input("date1 like 01/01/0000 "))
except:
    date1 = str(input("date1 like 01/01/0000 "))
try:
    date2 = str(input("date2 like 01/01/0000 "))
except:
    date2 = str(input("date2 like 01/01/0000 "))
    
params={
"api_key": 'IBFP-FDUlIyAnY_mJuzIjg',
"page": 1,
"page_size":25000,
'q[transaction_date_gteq]':date1,
'q[transaction_date_lteq]':date2,
'q[state_code_in][]':'TN',
"q[transaction_type_in][]":"MORTGAGE", 
"q[company_tags_in][]":"private_lender",
}
data_array =[]
response = requests.get(url,params=params)
if response.status_code == 200:
    # Process the response data (assuming it's JSON)
    data = response.json()
    transactions = data["transactions"]
    for t in transactions:
        data_array.append(t)
else:
    # Print an error message if the request was not successful
    print('Error:', response.reason)    
print(len(data_array))
contactdate1=date1.replace("/",".")
contactdate2=date2.replace("/",".")
csv_name= f'TN {contactdate1} - {contactdate2}.csv'
with open(csv_name, 'w', newline='\n')as file:
    fieldnames = ['fc_transaction_id', 'Scrape LLC', 'Lender', 'state', 'county', 'msa', 'recorded date', 'updated at','days updated apart']
    wright = csv.DictWriter(file, fieldnames=fieldnames)
    wright.writeheader()
    for data in data_array:
        # borrower = ''
        # companies = data['transaction_meta']['cross_companies']
        # if companies == None:
        #     continue
        # elif companies:
        #     for comps in companies:
        #         # pp.pprint(comps)
        #         # print("-------------------------")
        #         if comps['tags'] is None:
        #             borrower=comps['party_name']
        #         elif 'loan_buyer' not in comps['tags'] and 'private_lender_borrower' in comps['tags'] and 'borrower' in comps['tags']:
        #             borrower=comps['party_name']
        #         elif 'private_lender' in comps['tags'] or 'loan_buyer' in comps['tags']:
        #             lender = comps['party_name']

            # print(recorded_date) 
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
        "fc_transaction_id": data['∩╗┐fc_transaction_id'],
        "Scrape LLC": data['grantor'],
        "Lender": data["grantee"],
        "state": data["state_name"],
        "county": data["county"],
        "msa": data["msa_name"],
        "recorded date": str(recorded_date),
        "updated at": str(updated),
        "days updated apart": str(days)
        })
    