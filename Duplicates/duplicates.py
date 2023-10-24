import csv
import re
strip_NonNumber = r'\d+'
phone_number_format = r'(\d{3})(\d{3})(\d{4})'

lister = []
new_contacts=[]
good_number=[]
good_full=[]
bad_nums = []
final_contact=[]
contacts=[]
with open('contacts.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
with open('new.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    new_contacts=list(my_dict)
for li in lister:
    first=li["First Name"]
    last=li['Last Name']
    full=li['Full name']
    contact_id = li["Record ID"]
    extra=f'{first} {last}'
    phone_number = li["Phone Number"]
    numeric_digits = ''.join(re.findall(strip_NonNumber, phone_number))
    li["Phone Number"] = numeric_digits
    phone_number = li["Phone Number"]
    if len(phone_number) == 10:
        formatted_number = re.sub(phone_number_format, r'(\1) \2-\3', phone_number)
        x = formatted_number
        li["Phone Number"] =x
        phone_number =li["Phone Number"]
        bad_dict={
            "Fname":first,
            "Lname":last,
            "Ffull":full,
            "extra": extra,
            "phone":phone_number,
            "Record ID": contact_id
            }
        contacts.append(bad_dict)
    elif len(phone_number) == 11:
        phone_number = phone_number[1:]
        formatted_number = re.sub(phone_number_format, r'(\1) \2-\3', phone_number)
        x = formatted_number
        li["Phone Number"]=x
        phone_number=li["Phone Number"]
        bad_dict={
            "Fname":first,
            "Lname":last,
            "Ffull":full,
            "extra": extra,
            "phone":phone_number,
            "Record ID": contact_id
            }
        contacts.append(bad_dict)
    else: 
        bad_dict={
            "Fname":first,
            "Lname":last,
            "Ffull":full,
            "extra": extra,
            "phone":'',
            "Record ID": contact_id
            }
        contacts.append(bad_dict)
        
for new in new_contacts:
    new_phone = new["Phone number"]
    new_first = new["First Name"]
    new_last=new['Last Name']
    ext=new["Full Name"]
    new_full = f'{new_first} {new_last}'
    phone_exists = next((contact for contact in contacts if contact["phone"] == new_phone), None)
    full_name_exists = next((contact for contact in contacts if contact["Ffull"] == new_full), None)
    extra_full_name_exists = next((contact for contact in contacts if contact["extra"] == new_full), None)
    ext_extra_name_exists = next((contact for contact in contacts if contact["extra"] == ext), None)
    if phone_exists:
        new["Record ID"] = phone_exists.get("Record ID", None)
        final_contact.append(new)
    elif full_name_exists:
        new["Record ID"] = full_name_exists.get("Record ID", None)
        final_contact.append(new)
    elif extra_full_name_exists:
        new["Record ID"] = extra_full_name_exists.get("Record ID", None)
        final_contact.append(new)
    elif ext_extra_name_exists:
        new["Record ID"] = ext_extra_name_exists.get("Record ID", None)
        final_contact.append(new)
    else:
        new['Record ID'] = ''
        final_contact.append(new)
    

def witch_queen():
    with open('output.csv','w',encoding="cp437",newline='\n') as f:
        fieldnames = ['fc_transaction_id','Last Name','First Name',"Full Name",'Address', 'State', 'City', 'Zip','Phone number','Phone 2','Prem Email',
        'Email0', "MS Lender", "MS County", "MS Statistical Area", "Notes", "Lead Source","MS FC Recorded Date", "Record ID"]
        wright = csv.DictWriter(f, fieldnames=fieldnames)
        wright.writeheader()
        for n in final_contact:
            print(n)
            wright.writerow({"fc_transaction_id": n["fc_transaction_id"], 
            "First Name": n["First Name"],
            "Last Name": n["Last Name"],
            "Full Name": n['Full Name'],
            "Address": n["Address"],
            "State": n["State"],
            "City": n["City"],
            "Zip": n["Zip"],
            "Phone number": n["Phone number"],
            "Phone 2": n["Phone 2"],
            "Prem Email": n["Prem Email"],
            "Email0": n["Email0"],
            "MS Lender": n["MS Lender"],
            "MS County": n["MS County"],
            "MS Statistical Area": n["MS Statistical Area"],
            "Notes": n["Notes"],
            "MS FC Recorded Date": n["MS FC Recorded Date"],
            "Lead Source": "Market Sizing",
            "Record ID": n["Record ID"] 
            })


witch_queen()

