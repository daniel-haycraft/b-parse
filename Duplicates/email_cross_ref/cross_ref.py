import csv

final_contact = []
row=0
with open('all.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
with open('crossreff.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    emails=list(my_dict)

def email_looker():
    for mail in emails:
        print(mail["Email"])
        mail_exists = next((ex for ex in lister if ex["Email"] == mail["Email"]), None)
        if mail_exists:
            mail["Record ID"] = mail_exists.get("Record ID", None)
            mail["hs_Email"] = mail_exists.get("Email", None)
            mail["hsPhone"]=mail_exists.get("Phone Number", None)
            mail["First"]=mail_exists.get("First Name", None)
            mail["Last"]=mail_exists.get("Last Name", None)
            mail["Lead Source"]=mail_exists.get("Lead Source", None)
            final_contact.append(mail)
        else:
            mail["Record ID"] = ''
            mail["hs_Email"] = ''
            mail["hsPhone"]=''
            mail["First"]=''
            mail["Last"]=''
            mail["Lead Source"]=''
            final_contact.append(mail)
    print(final_contact)
print(email_looker())
with open("ref_complete.csv", 'w', newline="\n", encoding="cp437") as f:
    fieldnames = ["Record Id", "Loan Number", "Hs_First", "Hs_Last",'csv full',"csv first", 
    "csv last", "csv phone","Hs_Phone","hs_Email", "Email", "Lead Source"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for final in final_contact:
        wright.writerow({
        "Loan Number": final['Loan Number'],
        "Record Id": final["Record ID"],
        "Email": final["Email"],
        "hs_Email": final['hs_Email'],
        "Hs_First": final["First"],
        "Hs_Last": final["Last"],
        "csv full": final['Full Name'],
        "csv first":final["First Name"],
        "csv last":final["Last Name"],
        "csv phone": final["Phone Number"],
        "Hs_Phone": final["hsPhone"],
        "Lead Source": final["Lead Source"]
        })
        