import requests
import json
import pprint
import os
import csv
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
    "galaxy-ap-name": "capfund1",
    "galaxy-ap-password": "67ba081cb67e4dd9812d454998f02966",
    "galaxy-search-type": "Person"
}
parry=[]

no_pass=[]
not_sure=[]

def delta():
    with open('Wrong Number Correction.csv', 'w', newline='\n') as file:
        # Record ID - Contact,First Name,Last Name,Email,Phone number,Contact owner,Company name
        # 'Mailing Address','Mailing City','Mailing State','Mailing Zip'

        fieldnames = ['Record ID - Contact','Last Name','First Name','Phone number','Phone 2','Prem Email',
        'Market Sizing Email 2', 'Replaced Phone Number', "Number of Associated Deals"]

        wright = csv.DictWriter(file, fieldnames=fieldnames)
        wright.writeheader() 
        row=1
        for li in list_dict:
            if li['First Name']== '' or li['Last Name'] == '':
                continue

            firstN = li['First Name']
            lastN = li["Last Name"]
            # phone_number=li['Phone Number']    
            address = li['Street Address']        
# Record ID - Contact,First Name,Last Name,Contact owner,State/Region,Email,Street Address,City
                # "Address": address,
            myson= {
                "FirstName": firstN,
                "LastName": lastN,
                "Address": address, 
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
                print("'persons' key is missing in this entry, skipping to next iteration")
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
            wright.writerow({"Record ID - Contact": li['Record ID - Contact'], 
            "Last Name": lastN,
            "First Name":firstN,
            "Phone number": new_phone[0]if new_phone else '',
            "Phone 2": new_phone[1] if len(new_phone)> 1 else '',
            "Prem Email":new_email[0]if new_email else '',
            "Market Sizing Email 2": new_email[1] if len(new_email)> 1 else '',
            "Number of Associated Deals": li["Number of Associated Deals"]
            })
            
            print(row, ' out of ',len(list_dict), ' fetched and processed ')
            row+=1

if __name__ == "__main__":
    list_dict = []
    with open("wrongo.csv", "r") as file:
        my_dict = csv.DictReader(file)
        list_dict = list(my_dict)
    delta()