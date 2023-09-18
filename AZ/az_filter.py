import csv
list_az=[]
with open("Daniel's python name and address locator\AZ\AZ for borrows.csv", 'r') as az:
    my_az = csv.DictReader(az)
    list_az = list(my_az)
# im going to split by ;
#check if name is in grantor and if it is pop it!
from fuzzywuzzy import fuzz
lenders=[]
threshold = 70
def check_yo_shi():
    with open('AZ.csv',"w", newline='\n') as az:
        fieldnames = ['fc_transaction_id','grantor', 'Lend']
        write = csv.DictWriter(az, fieldnames=fieldnames)
        write.writeheader()
        for li in list_az:
            if len(li['Name']) > 1:
                lenders.append(li["Name"])
        for li in list_az:
            splitter = li['grantor'].split(';')
            for split in splitter:
                best_match = max(lenders, key=lambda grantor: fuzz.token_sort_ratio(split, grantor))
                similarity = fuzz.token_sort_ratio(split, best_match)
                if similarity >= threshold:
                    index = splitter.index(split)
                    new=splitter.pop(index)
                    write.writerow({'fc_transaction_id': li['fc_transaction_id'], 'grantor': splitter[0] if len(splitter) > 0 and splitter[0] != '' else splitter, 'Lend': split})


check_yo_shi()

