from schemas import Zipcode
import json
import csv

lister = []
with open('ruca.csv',"r",encoding="cp437") as f:
    my_dict=csv.DictReader(f)
    lister=list(my_dict)
for row in lister:
    row["ZIPcode"] = row.pop("∩╗┐ZIPCode")  # remove BOM + rename
for row in lister:
    Zipcode.create(
        zipp=int(row["ZIPcode"]),
        State=row["State"],
        ZipType=row["ZIPCodeType"],
        POName=row["POName"],
        PrimR=int(row["PrimaryRUCA"]),
        SecondR=float(row["SecondaryRUCA"])
    )

