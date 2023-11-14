import csv
list_az=[]
with open("AZ.csv", 'r') as az:
    my_az = csv.DictReader(az)
    list_az = list(my_az)

print(list_az)
# im going to split by ;
#check if name is in grantor and if it is pop it!
from fuzzywuzzy import fuzz
lenders=[]
threshold = 75
def check_yo_shi():
    with open('AZ0.csv',"w", newline='\n') as az:
        fieldnames = ['ï»¿fc_transaction_id','grantor', 'Lend', 'bad', 'og_grantor', 'clean']
        write = csv.DictWriter(az, fieldnames=fieldnames)
        write.writeheader()
        for li in list_az:
            if len(li['Name']) > 1:
                lenders.append(li["Name"])
        for li in list_az:
            splitter = li['grantor'].split(';')
            if len(splitter) == 1:
                write.writerow({'ï»¿fc_transaction_id': li['ï»¿fc_transaction_id'], 'grantor': splitter[0] if len(splitter) > 0 and splitter[0] != '' else splitter,"Lend": li['Name'], 'bad': splitter, 'clean':'YES'})
            elif len(splitter):
                for split in splitter:
                    best_match = max(lenders, key=lambda grantor: fuzz.token_sort_ratio(split, grantor))
                    similarity = fuzz.token_sort_ratio(split, best_match)
                    if similarity > threshold:
                        index = splitter.index(split)
                        new=splitter.pop(index)
                        write.writerow({'ï»¿fc_transaction_id': li['ï»¿fc_transaction_id'], 
                        'grantor': splitter[0] if len(splitter) > 0 and splitter[0] != '' else splitter,
                        'Lend': split if split else ' ', 'bad': li["Name"], 'og_grantor': li['grantor']})
                    else: 
                        write.writerow({'ï»¿fc_transaction_id': li['ï»¿fc_transaction_id'], 'bad': li["Name"], "og_grantor": li['grantor'], "clean": "No"})


check_yo_shi()

