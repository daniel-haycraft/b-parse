import requests
import json
import pprint
import csv
import os


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
url = "https://api.galaxysearchapi.com/DebtSearch/V2"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "galaxy-ap-name": 'capfund1',
    "galaxy-ap-password":'67ba081cb67e4dd9812d454998f02966',
    "galaxy-search-type": "DebtV2",
}

request_json = {
    "Ssn": '466-98-9458',
    "AddressLine2": "AZ",
    "Page": 1,
    "ResultsPerPage": 5,
    "DebtType": 2
}
res = requests.post(url, headers=headers, json=request_json)

the_sonj= res.text
data = json.loads(the_sonj)
pp.pprint(data)