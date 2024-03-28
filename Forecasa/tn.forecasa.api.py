import requests
import json
import pprint
import csv
import os
from datetime import datetime as dt
pp = pprint.PrettyPrinter(0)
key = "IBFP-FDUlIyAnY_mJuzIjg"
url = "https://webapp.forecasa.com/api/v1/transactions"
params={
"api_key": 'IBFP-FDUlIyAnY_mJuzIjg',
"page": 1,
"page_size":10000,
'q[transaction_date_gteq]': '01/01/2023',
'q[transaction_date_lteq]': '01/01/2024',
'q[state_code_in][]':'TN',
# 'q[fc_transaction_id_cont]':'Tn',
# "q[county_in][]":"s_Maricopa-Az",
# "q[county_in][]":"s_Mohave-Az",
# "q[county_in][]":"s_Pima-Az",
# "q[county_in][]":"s_Pinal-Az",
# "q[county_in][]":"s_Yavapai-Az",
# "q[county_in][]":"s_Yuma-Az",
# "q[county_in][]":"s_Coconino-Az",
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
        
        if t['state_name'] == 'TENNESSEE':
            data_array.append(t)
else:
    # Print an error message if the request was not successful
    print('Error:', response.reason)

    
print(len(data_array))
with open("fork.csv", 'w', newline='\n')as file:
    fieldnames = ['fc_transaction_id', 'Scrape LLC','Secondary LLC', 'Lender', 'state', 'county', 'msa', 'recorded date', 'updated at','days updated apart']
    wright = csv.DictWriter(file, fieldnames=fieldnames)
    wright.writeheader()
    for data in data_array:
        # print('Data')
        # pp.pprint(data)
        # print('Companies')
        # pp.pprint(companies)
        companies = data['transaction_meta']['companies']
        if companies == None:
            continue
        else:
            for comps in companies:
                # print("comp!")
                # print(comps)
                if comps['tags'] == None:
                    borrower=comps['party_name']
                elif 'loan_buyer' not in comps['tags'] and 'private_lender_borrower' in comps['tags'] and 'borrower' in comps['tags']:
                    borrower=comps['party_name']
                    # print(borrower, comps['tags'])
                elif 'private_lender' in comps['tags'] or 'loan_buyer' in comps['tags']:
                    lender = comps['party_name']

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
            if days >= 90:
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