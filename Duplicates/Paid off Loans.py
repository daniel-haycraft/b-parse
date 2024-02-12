import pyodbc
import csv
cnxn = pyodbc.connect("DRIVER={CData ODBC Driver for HubSpot}; DATABASE=CData HubSpot Sys; Auth Scheme=OAuth; OAuth Settings Location='C:/Users/Daniel Haycraft/Desktop/newstuff/OAuth.txt'")
cursor = cnxn.cursor()

x=cursor.execute('SELECT "FundPropertyID", "Loan Number" FROM Deals')
row = 0
with open("paidoffdeals", 'w', encoding="cp437",newline='\n') as f:
    fieldnames = ["Property ID", "Loan Number"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for c in x:
        propertyid=str(c[0])
        propertyid.split(".")
        print(propertyid)
        # wright.writerow({
        # "Property ID": propertyid,
        # "Loan Number": c[1]
        # })




















