import csv
list_az=[]
with open("no lender.csv", 'r') as az:
    my_az = csv.DictReader(az)
    list_az = list(my_az)

print(list_az)
# im going to split by ;
#check if name is in grantor and if it is pop it!
from fuzzywuzzy import fuzz
lenders=[]
threshold = 60
def check_yo_shi():
    with open('AZ.csv',"w", newline='\n') as az:
        fieldnames = ['transactions','grantor', 'Lend', 'bad']
        write = csv.DictWriter(az, fieldnames=fieldnames)
        write.writeheader()
        for li in list_az:
            if len(li['Name']) > 1:
                lenders.append(li["Name"])
        for li in list_az:
            splitter = li['grantor'].split(';')
            if len(splitter) == 1:
                write.writerow({'transactions': li['ï»¿transactions'], 'grantor': splitter[0] if len(splitter) > 0 and splitter[0] != '' else splitter,
                    'Lend': split, 'bad': splitter})
            elif len(splitter):
                for split in splitter:
                    best_match = max(lenders, key=lambda grantor: fuzz.token_sort_ratio(split, grantor))
                    similarity = fuzz.token_sort_ratio(split, best_match)
                    if similarity >= threshold:
                        index = splitter.index(split)
                        new=splitter.pop(index)
                        write.writerow({'transactions': li['ï»¿transactions'], 'grantor': splitter[0] if len(splitter) > 0 and splitter[0] != '' else splitter,
                        'Lend': split, 'bad': splitter})


check_yo_shi()

