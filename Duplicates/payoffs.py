import pyodbc
import csv
import random
from datetime import datetime as timeforce
cnxn = pyodbc.connect("DRIVER={CData ODBC Driver for HubSpot}; DATABASE=CData HubSpot Sys; Auth Scheme=OAuth; OAuth Settings Location='C:/Users/Daniel Haycraft/Desktop/newstuff/OAuth.txt'")
cursor = cnxn.cursor()
randy=random.randint(500, 150000)
sql=cursor.execute('SELECT "Id", "Loan Number", "Deal Name", "Deal Stage", "FundPropertyID" FROM Deals')
row = 0
dealupdatelist = []

today=timeforce.today().date().strftime("%m.%d.%Y")
# Read the CSV file and create a lookup dictionary
loan_dict = {}
with open("deal input.csv", 'r', encoding="cp437") as f:
    my_dict = csv.DictReader(f)
    for row in my_dict:
        caps_id = str(row["caps_id"]).strip()  # Strip spaces
        loan_number = str(row["loan_number"]).strip() 
        loan_dict[(caps_id, loan_number)] = row 

# Compare SQL results with loan list
for c in sql:
    if c[3] == "closedwon" or c[3] == "2292223":  # Check deal stage
        deal_id = str(c[0])  # ID
        loan_number = str(c[1]).strip()  # Loan Number
        fund_property_id = str(int(c[4])).strip() # Ensure this is a string for comparison
            # Use the tuple to check for a match in the dictionary
        if (fund_property_id, loan_number) in loan_dict:
            loan_details = loan_dict[(fund_property_id, loan_number)]
            print(f"Match found! ID: {deal_id}, FundPropertyID: {fund_property_id}, Loan Number: {loan_number}, Caps ID: {loan_details['caps_id']}, Loan Number: {loan_details['loan_number']}")
                    
            # with open(f"deals{today};{randy}.csv", 'w', encoding="cp437",newline='\n') as f:
            #     fieldnames = ["Record Id","Deal Name", "Loan Number", "Payoff Method", "Sold Value", "Cap ID", "Orginal Maturity Date", "Payoff Date", "Deal Stage"]
            #     wright = csv.DictWriter(f, fieldnames=fieldnames)
            #     wright.writeheader()
            #     write.writerow({
            #         "Record Id": c[0],
            #         "Loan Number": c[1],
            #         "Deal Name": c[2],
            #     })



# with open("all.csv", 'w', encoding="cp437",newline='\n') as f:
#     fieldnames = ["Record ID","First Name","Last Name","Phone Number","Full Name","Email", "Contact Owner", "Lead Source"]
#     wright = csv.DictWriter(f, fieldnames=fieldnames)
#     wright.writeheader()
#     for c in x:
#         try:
#             if c[1] != '' and c[4] != '' and c[5] != '':
#                 wright.writerow({
#                 "First Name": c[4],
#                 "Last Name": c[5],
#                 "Full Name": c[2],
#                 "Email": c[0],
#                 "Record ID": c[3],
#                 "Phone Number":c[1],
#                 "Contact Owner": c[6],
#                 "Lead Source": c[7],
#                 })
#         except:
#             row+=1
#             print(row)
#         else:
#             row+=1
#             print(row)
#             continue




















