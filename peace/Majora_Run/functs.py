import csv
def splitting_chars_only(sp):
    split_city = sp[-1].split(",")
    split_state = split_city[-1].strip()
    split_state = split_state.split(" ")
    sp.append(split_city[0])
    sp.append(split_state[0])
    try:
        sp.append(split_state[1])
    except:
        return 'move on'
    if len(sp) == 5:
        sp.remove(sp[1])
    else:
        # print(sp,1)
        sp.remove(sp[2])
        # print(sp, 2)
    return sp

def joining_ste_chars_four(lst):
    first_part = lst[1]
    second_part = lst[2]
    new = first_part+" " +second_part
    lst.remove(first_part)
    lst[1] = new
    # print( lst)
    return lst

def joining_ste_nums_three(lst):
    first_part = lst[0]
    second_part = lst[1]
    new = first_part+" " +second_part
    lst.remove(first_part)
    lst[0] = new
    # print( lst)
    return lst

def writer_row(majoras_mask):
    with open('r2_py2.csv', "w", newline='\n', encoding="cp437") as csvfile:
        fieldnames = ['fc_transaction_id', 'Full Name', 'Name', 'Street Address','City', 'State', 'Zip', 'Notes']
        write = csv.DictWriter(csvfile, fieldnames=fieldnames)
        write.writeheader()
        for li in majoras_mask:
            write.writerow({'fc_transaction_id': li['fc_transaction_id'], 
                            'Full Name': li['Full Name'],
                            'Name': li['Name'],
                            'Street Address':li['Street Address'],
                            'City': li['City'],
                            'State':li['State'],
                            'Zip':li['Zip'],
                            })
company_tags = ["LLC", "LP", "LLP", "Inc", "Corporation", "Systems", "Corp", "Ltd.", "L.L.C", "Co.", "GP", "PC", "PLLC", "PA", "LLLP", "DBA", "P.C.", "P.L.L.C.", "P.A.", "LLLLP", "S-Corp", "C-Corp", "SPC", "SCorp", "B-Corp", "D/B/A"]

def detecting_tags(word):
    word_2 = str(word[0])
    for tag in company_tags:
        found_match = False
        if tag in word_2:
            return word.remove(word_2)