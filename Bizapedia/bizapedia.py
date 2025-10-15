import requests
import json
import pprint
import csv
import os
pp = pprint.PrettyPrinter(50)
from request import ProApiClient
def state_abv(state):
        state_revision = {
            'Alabama': 'AL',
            'Alaska': 'AK',
            'Arizona': 'AZ',
            'Arkansas': 'AR',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'Delaware': 'DE',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Hawaii': 'HI',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Iowa': 'IA',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Maine': 'ME',
            'Maryland': 'MD',
            'Massachusetts': 'MA',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Mississippi': 'MS',
            'Missouri': 'MO',
            'Montana': 'MT',
            'Nebraska': 'NE',
            'Nevada': 'NV',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'New York': 'NY',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Vermont': 'VT',
            'Virginia': 'VA',
            'Washington': 'WA',
            'West Virginia': 'WV',
            'Wisconsin': 'WI',
            'Wyoming': 'WY',
            'District of Columbia': 'DC',
            'American Samoa': 'AS',
            'Guam': 'GU',
            'Northern Mariana Islands': 'MP',
            'Puerto Rico': 'PR',
            'United States Minor Outlying Islands': 'UM',
            'Virgin Islands, U.S.': 'VI',
        }
        return state_revision.get(state, "State not found")
lister=[]
with open('forecasa.csv',"r", encoding='latin1') as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
# create a csv file that checks for duplicate id's

def process_companies(lister, output_file):
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["Error", "fc_transaction_id", "Company", "State", "Property Address", "City", "Zip", "Full Name", "First Name", "Last Name", "Notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for li in lister:
            note = f""" llc: {li['name']}\n, 
            last mortgage transaction: {li['last_mortgage_date']},\n
            average amount spent per loan: {li['average_mortgage_amount']},\n
            Last Lender used: {li['last_lender_used']},\n
            # of Mortgage Transactions: {li['mortgage_transactions']},\n
            Upcoming maturities: "{li["upcoming_maturities"]}\n""" 
            process_company_entry(li, writer, note)

def process_company_entry(entry, writer,note):
    global err
    err = False
    company_name = entry.get("name", "")
    state = entry.get("last_state", "").title()
    abv_state = state_abv(state)
    
    try:
        output = ProApiClient.lookup_companies(company_name=company_name, city="", postal_abbreviation=abv_state)
        data = json.loads(output)
        print(data)
    except Exception as e:
        err = True
        print(f"Error processing company {company_name}: {e}")
        return
    for comp in data.get("Companies", []):
        if "Principals" in comp and comp["Principals"]:
            
            principal = comp["Principals"][0]
            print(principal)  # Get the first principal
            writer.writerow({
                "Error": err,
                "Company": company_name.title(),
                "fc_transaction_id": entry.get("id", ""),
                "Property Address": principal.get("AddressLine1", "").title(),
                "City": principal.get("City", "").title(),
                "State": principal.get("StateProvince", "").title(),
                "Zip": principal.get("PostalCode", "").title(),
                "Full Name": principal.get("PrincipalName", "").title(),
                "First Name": principal.get("FirstName", "").title(),
                "Last Name": principal.get("LastName", "").title(),
                "Notes": note
            })
        break
         
process_companies(lister, "forecasa_ready4skip.csv")
print(ProApiClient.get_api_call_count())