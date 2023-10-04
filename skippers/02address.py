import requests
import json
import pprint
import os
import csv
from pprint import PrettyPrinter
from hocus import username, password
pp = PrettyPrinter(0)
def check_names_to_full(names, full):
    arry=[]
    for n in names:
        if n.lower() == full.lower():
            arry.append(n.upper())
            return(arry) 
def go_to_first_last_name(iterable):
    for i in iterable:
        return i['firstName'], i['lastName']
url = "https://api.galaxysearchapi.com/PropertyV2Search"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "galaxy-ap-name": username,
    "galaxy-ap-password": password[0],
    "galaxy-search-type": "PropertyV2"
}
person_url = "https://api.galaxysearchapi.com/PersonSearch"
person_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "galaxy-ap-name": username,
    "galaxy-ap-password": password[0],
    "galaxy-search-type": "Person"
}
parry=[]
no_pass=[]
not_sure=[]
filtered_id= 0
def delta():
    with open('address_mortis.csv', 'w', newline='\n') as file:
        fieldnames = ['ï»¿fc_transaction_id','Last Name','First Name','Address', 'State', 'City', 'Zip','Phone number','Phone 2','Prem Email',
        'Email0']
        wright = csv.DictWriter(file, fieldnames=fieldnames)
        wright.writeheader() 
        row=1
        for li in list_dict:
            address = li['Address']
            city = li["City"]
            state = li["State"] 
            zip_ = li["Zip"]
            city_state = f"{city}, {state} {zip_}"      
            myson= {
                "FirstName": "",
                "LastName": "",
                "AddressLine1": address,
                "AddressLine2": city_state,
                "ResultsPerPage": 1,
                "Page": 1,
            }

            res = requests.post(url, headers=headers, json=myson)
            the_sonj= res.text
            data = json.loads(the_sonj)
            try:
                bob = [x for x in data['propertyV2Records']]
            except:
                print('had me at BOB')
                continue
            if bob == []:
                continue

            prop=bob[0]['property']
            current_owner = prop['summary']['currentOwners'][0]
            id_= current_owner['name']['tahoeId']
            if id_ == None:
                print('ugh')
                row +=1
                continue
            else:
                filtered_id = id_
            jpersOn = {
                "tahoeId": filtered_id,
                "Includes": ["PhoneNumbers", "EmailAddresses"],
                "FilterOptions": ['IncludeSevenDigitPhoneNumbers', 'IncludeLatestRecordOnly'],
                "Page": 1,
            }    
            try:

                the_father = requests.post(person_url, headers=person_headers, json=jpersOn)
            except:
                print('skipper')
                row +=1
                continue
            the_brother=the_father.text
            the_daughter = json.loads(the_brother)
            try:
                ahsoka = the_daughter['persons']
                # Process divi_data here
            except KeyError:
                print("'persons' key is missing in this entry, skipping to next iteration")
                row +=1
                continue  # Move to the next iteration
# # -------------------------------------------------------------------------------------------------------------------------------------------------                
            new_email = []
            new_phone = []
            same = ''
            recorded_last= ''
            recorded_first =  ''
            top_results = []
            for soka in ahsoka:
                if len(top_results) == 2:
                    break
                top_results.append(soka)
            for top in top_results:
                recorded_first = top['name']['firstName']
                recorded_last = top['name']['lastName']
                emails = [x['emailAddress'] for x in top['emailAddresses']]
                phone_s = [x['phoneNumber'] for x in top['phoneNumbers']]
                if phone_s or emails:
                    new_email = emails[0:2]
                    new_phone = phone_s[0:2]
                    break
            wright.writerow({"ï»¿fc_transaction_id": li["fc_transaction_id"], 
            'Last Name': recorded_last,
            'First Name': recorded_first,
            "Address": li['Address'],
            "City": li["City"],
            "State": li["State"],
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
    with open("Adresses.csv", "r") as file:
        my_dict = csv.DictReader(file)
        list_dict = list(my_dict)
    delta()