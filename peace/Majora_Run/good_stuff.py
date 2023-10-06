from Majora_Run.functs import splitting_chars_only, joining_ste_chars_four, joining_ste_nums_three, writer_row, detecting_tags
import csv
from Majora_Run.structer import Append_to_csv as Charlie

bad_full_array = []
bad_mailing_array=[]
def alpha(list_dict):
    for li in list_dict:
        li.update({"Name":" ", "Address": " ", 
                   "City":" ", "State": " ", 
                   "Zip": " ",
                    'Mailing Street Address': " ",
                    'Mailing City': " ",
                    'Mailing State': " ",
                    'Mailing Zip': " "})
        splitter = li['Full Name'].split("\n")
        detecting_tags(splitter)
        length_of_splitter = len(splitter)
        print(splitter) 
        if len(splitter) <= 1 or splitter[0] == '':
            print(len(splitter), "1 or less than 1")
        elif splitter[0][0].isnumeric() == False:
            if length_of_splitter == 3:
                splitting_chars_only(splitter)
                joiner =  ", ".join(splitter)
                Charlie.handle_the_update(li, fullname=joiner, name=splitter[0], addy=splitter[1], 
                city=splitter[2], state=splitter[3], zip_=splitter[4])
            elif length_of_splitter == 4:
                joining_ste_chars_four(splitter)
                splitting_chars_only(splitter)
                joiner = ", ".join(splitter)
                Charlie.handle_the_update(li, fullname=joiner, name=splitter[0], addy=splitter[1], 
                city=splitter[2], state=splitter[3], zip_=splitter[4])
        elif splitter[0][0].isnumeric():
                if len(splitter) == 2:
                    splitter
                    splitting_chars_only(splitter)
                    joiner = ", ".join(splitter)
                    Charlie.handle_the_update(li, fullname=joiner, name=' ', addy=splitter[0], 
                    city=splitter[1], state=splitter[2], zip_=splitter[3])
                elif len(splitter) == 3:
                    joining_ste_nums_three(splitter)
                    splitting_chars_only(splitter)
                    joiner = ", ".join(splitter)
                    Charlie.handle_the_update(li, fullname=joiner, name=' ', addy=splitter[0], 
                    city=splitter[1], state=splitter[2], zip_=splitter[3])
                else:
                    bad_full_array.append(splitter)
        else:
            continue
    writer_row(list_dict)
    
def bravo(list_dict):
    for li in list_dict:
        mailing_spliter = li["Mailing Address"].split("\n")
        if len(mailing_spliter) == 2:
            splitting_chars_only(mailing_spliter)
            joiner = ", ".join(mailing_spliter)
            li["Mailing Address"]= joiner
            li['Mailing Street Address']= mailing_spliter[0]
            li['Mailing City']= mailing_spliter[1]
            li['Mailing State']= mailing_spliter[2]
            li['Mailing Zip']= mailing_spliter[3]
        elif len(mailing_spliter) == 3:
            joining_ste_nums_three(mailing_spliter)
            splitting_chars_only(mailing_spliter)
            joiner = ", ".join(mailing_spliter)
            li["Mailing Address"] = joiner
            li['Mailing Street Address']= mailing_spliter[0]
            li['Mailing City']= mailing_spliter[1]
            li['Mailing State']= mailing_spliter[2]
            li['Mailing Zip']= mailing_spliter[3]
            
        else:
            bad_mailing_array.append(mailing_spliter)
    writer_row(list_dict)

        



