import csv
from Majora_Run.good_stuff import alpha, bravo
def up_K():
    x = input(str("send me the path to csv file"))
    x=''.join(i for i in x if i not in '""')
    list_dict = []
    with open(x, "r") as file:
        my_dict = csv.DictReader(file)
        list_dict = list(my_dict)
    alpha(list_dict)
    bravo(list_dict)
