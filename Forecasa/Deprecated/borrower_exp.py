import requests
import json
import pprint
import csv
import os
from datetime import datetime as dt
from difflib import SequenceMatcher
pp = pprint.PrettyPrinter(0)
from fuzzywuzzy import fuzz
exp=[]
caps=[]


company_tags = ["LLC", "LP", "LLP", "Inc", "Corporation", "Systems", "Corp", "Ltd.", "L.L.C", "Co.", "GP", "PC", "PLLC", "PA", "LLLP", "DBA", "P.C.", "P.L.L.C.", "P.A.", "LLLLP", "S-Corp", "C-Corp", "SPC", "SCorp", "B-Corp", "D/B/A", "Real Estate"]

with open('borrower_exp.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    exp=list(my_dict)
with open('Data Management.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    caps=list(my_dict)
# print(exp)

for e in exp:
     e['principal_name']=e['principal_name'].title()
for c in caps:
    c["Full Name"] = f"{c['Borrower First Name'].title()} {c['Borrower Last Name'].title()}"
buyers_list = []
for forecasa in exp: 
    f_name = forecasa["principal_name"]
    for data in caps:
        if f_name == data["Full Name"]:
            buyer_data = {
                "Caps Name": data["Full Name"],
                "Caps ID": data["ID"],
                "Loan Number": data["Loan #"],
                "Forecasa Name": f_name,
                "Mortgage Transactions": forecasa["mortgage_transactions"],
                "Transactions as Buyer": forecasa["transactions_as_buyer"],
            }
            buyers_list.append(buyer_data)
            break
        else:
            continue
with open("forecasaXcaps.csv","w",newline='\n')as f:
    fieldnames = ["Caps Name","Caps ID","Loan Number", "Forecasa Name", "Mortgage Transactions", "Transactions as Buyer"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for buyer in buyers_list:
        wright.writerow({
            "Caps Name": buyer["Caps Name"],
            "Caps ID": buyer["Caps ID"],
            "Loan Number": buyer["Loan Number"],
            "Forecasa Name": buyer["Forecasa Name"],
            "Mortgage Transactions": buyer["Mortgage Transactions"],
            "Transactions as Buyer": buyer["Transactions as Buyer"]
        })