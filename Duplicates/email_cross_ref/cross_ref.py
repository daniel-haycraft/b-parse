import csv

final_contact = []
row=0
with open('all.csv',"r", encoding='latin1') as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
with open('crossreff.csv',"r", encoding='latin1') as f:
    my_dict=csv.DictReader(f)
    emails=list(my_dict)

def email_looker():
    for mail in emails:
        print(mail["Email"])
        if len(mail["Email"])<=1:
            mail["Record ID"] = ''
            mail["hs_Email"] = ''
            mail["hsPhone"]=''
            mail["First"]=''
            mail["Last"]=''
            mail["Lead Source"]=''
            final_contact.append(mail)
            print('Skipped')
            continue
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
with open("ref_complete.csv", 'w', encoding="UTF-8",newline="\n") as f:
    fieldnames = ["Contact Id","Association Label", "Loan Number", "Hs_First", "Hs_Last",'full',"first", 
    "last", "phone","Hs_Phone","hs_Email", "Email", "Lead Source", "Deal Id"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for final in final_contact:
        wright.writerow({
        "Loan Number": final['Loan Number'],
        "Contact Id": final["Record ID"],
        "Email": final["Email"],
        # "hs_Email": final['hs_Email'],
        # "Hs_First": final["First"],
        # "Hs_Last": final["Last"],
        "full": final['Full Name'],
        "first": final['First Name'],
        "last": final['Last Name'],
        "phone": final["Phone Number"],
        # "Hs_Phone": final["hsPhone"],
        # "Lead Source": final["Lead Source"],
        "Deal Id": final["ï»¿Deal Id"],
        "Association Label": final["Association Label"]
        })
        