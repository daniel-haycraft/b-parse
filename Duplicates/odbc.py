import pyodbc
import csv
cnxn = pyodbc.connect("DRIVER={CData ODBC Driver for HubSpot}; DATABASE=CData HubSpot Sys; Auth Scheme=OAuth; OAuth Settings Location='C:/Users/Daniel Haycraft/Desktop/newstuff/OAuth.txt'")
cursor = cnxn.cursor()

x=cursor.execute('SELECT "Email", "Phone Number", "Full Name", "Id", "First Name", "Last Name" FROM Contacts')

row = 0
with open("all.csv", 'w', encoding="cp437",newline='\n') as f:
    fieldnames = ["Record ID","First Name","Last Name","Phone Number","Full Name","Email"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for c in x:
        try:
            if c[1] != '' and c[4] != '' and c[5] != '':
                wright.writerow({
                "First Name": c[4],
                "Last Name": c[5],
                "Full Name": c[2],
                "Email": c[0],
                "Record ID": c[3],
                "Phone Number":c[1]
                })
        except:
            row+=1
            print(row)
        else:
            row+=1
            print(row)
            continue




















