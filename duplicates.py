import csv
import re
strip_NonNumber = r'\d+'
phone_number_format = r'(\d{3})(\d{3})(\d{4})'

lister = []
new_contacts=[]
good_number=[]
good_full=[]
bad_nums = []

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
    extra=f'{first} {last}'
    good_full.append(extra)
    good_full.append(full)
    phone_number = li["Phone Number"]
    numeric_digits = ''.join(re.findall(strip_NonNumbers, phone_number))
    li["Phone Number"] = numeric_digits
    phone_number = li["Phone Number"]
    if len(phone_number) == 10:
        formatted_number = re.sub(phone_number_format, r'(\1) \2-\3', phone_number)
        x = formatted_number
        li["Phone Number"] =x
        phone_number =li["Phone Number"]
        good_number.append(phone_number)
    elif len(phone_number) == 11:
        phone_number = phone_number[1:]
        formatted_number = re.sub(phone_number_format, r'(\1) \2-\3', phone_number)
        x = formatted_number
        li["Phone Number"]=x
        phone_number =li["Phone Number"]
        good_number.append(phone_number)
    else: 
        continue
final_contact=[]
for new in new_contacts:

    new_phone = new["Phone number"]
    new_first = new["First Name"]
    new_last=new['Last Name']
    new_full = f'{new_first} {new_last}' 
    if new_phone in good_number or new_full in good_full:
        bad_nums.append(new)
    else:
        final_contact.append(new)

with open('output.csv','w',encoding="cp437",newline='\n') as f:
    fieldnames = ['fc_transaction_id','Last Name','First Name',"Full Name",'Address', 'State', 'City', 'Zip','Phone number','Phone 2','Prem Email',
    'Email0', "MS Lender", "MS County", "MS Statistical Area", "Notes"]
    wright = csv.DictWriter(f, fieldnames=fieldnames)
    wright.writeheader()
    for n in final_contact:
        wright.writerow({"fc_transaction_id": n["∩╗┐fc_transaction_id"], 
        "First Name": n["First Name"],
        "Last Name": n["Last Name"],
        "Full Name": f'{n["First Name"]} {n["Last Name"]}',
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
        "Notes": n["Notes"]
        })




