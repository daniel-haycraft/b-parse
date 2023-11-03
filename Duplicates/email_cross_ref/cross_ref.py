import csv

final_contact = []
row=0
with open('../all.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
with open('crossreff.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    emails=list(my_dict)

def email_looker():
    for mail in emails:
        print(mail["∩╗┐Email"])
        phone_exists = next((ex for ex in lister if ex["Email"] == mail["∩╗┐Email"]), None)
        if phone_exists:
            mail["Record ID"] = phone_exists.get("Record ID", None)
            final_contact.append(mail)
        else:
            mail["Record ID"] = ''
            final_contact.append(mail)
    print(final_contact)
print(email_looker())
with open("ref_complete.csv", 'w', newline="\n") as f:
    fieldnames = ["Email", "Record Id"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for final in final_contact:
         wright.writerow({"Email": final["∩╗┐Email"], "Record Id": final["Record ID"]})
