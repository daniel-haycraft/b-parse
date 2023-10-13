import requests
import json
import pprint
import csv
import os
from hocus import username, password
pp = pprint.PrettyPrinter(0)
def check_names_to_full(names, full):
    arry=[]
    for n in names:
        if n.lower() == full.lower():
            arry.append(n.upper())
            return(arry)
def go_to_first_last_name(iterable):
    for i in iterable:
        return i['firstName'], i['lastName']
url = "https://api.galaxysearchapi.com/PersonSearch"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "galaxy-ap-name": username,
    "galaxy-ap-password":password[0],
    "galaxy-search-type": "Person",
}

parry=[]
no_pass=[]
not_sure=[]

def delta():
    with open('names thrawn.csv', 'w', newline='\n') as file:
        fieldnames = ['ï»¿fc_transaction_id','Last Name','First Name','Address', 'State', 'City', 'Zip','Phone number','Phone 2','Prem Email',
        'Email0']
        wright = csv.DictWriter(file, fieldnames=fieldnames)
        wright.writeheader() 
        row=1
        for li in list_dict:
            firstN= li["First Name"]
            lastN= li["Last Name"]
            address= li['Address']
            city= li["City"]
            state= li["State"] 
            city_state= f"{city}, {state}"      
            myson= {
                "FirstName": firstN,
                "LastName": lastN,
                "Address": address,
                "Addresses":[
                    {
                        "AddressLine2": city_state
                    }
                ],
                "Includes": ["PhoneNumbers", "EmailAddresses"],
                "FilterOptions": ['IncludeSevenDigitPhoneNumbers', 'IncludeLatestRecordOnly'],
                "Page": 1,
            }
            res = requests.post(url, headers=headers, json=myson)
            the_sonj= res.text
            data = json.loads(the_sonj)
            try:
                divi_data = data['persons']
                # Process divi_data here
            except KeyError:
                print("'persons' key is missing in this entry", "row: ", row)
                row+=1
                continue  # Move to the next iteration
            top_results = []
            for div in divi_data:
                if len(top_results) == 2:
                    break
                top_results.append(div)
            new_email = []
            new_phone = []
            same = ''
            for top in top_results:
                if top['name']['firstName'] == firstN or top['name']['lastName'] == lastN:
                    emails = [x['emailAddress'] for x in top['emailAddresses']]
                    phone_s = [x['phoneNumber'] for x in top['phoneNumbers']]
                    if phone_s or emails:
                        new_email = emails[0:2]
                        new_phone = phone_s[0:2]
                        break
            wright.writerow({"ï»¿fc_transaction_id": li['ï»¿fc_transaction_id3'], 
            "First Name": firstN,
            "Last Name": lastN,
            "Address": address,
            "State": state,
            "City": city,
            "Zip": li["Zip"],
            "Phone number": new_phone[0]if new_phone else '',
            "Phone 2": new_phone[1] if len(new_phone)> 1 else '',
            "Prem Email":new_email[0]if new_email else '',
            "Email0": new_email[1] if len(new_email)> 1 else '',
            })
            print(row, ' out of ',len(list_dict), ' fetched and processed ')
            row+=1
if __name__ == "__main__":
    list_dict = []
    with open("names.csv", "r") as file:
        my_dict = csv.DictReader(file)
        list_dict = list(my_dict)

    delta()