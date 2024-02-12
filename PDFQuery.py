import csv
from pdfquery import PDFQuery
from prettyprinter import pprint
import re
pdf = PDFQuery("Agent Owned Active Listings - GA.pdf")
pdf.load()

# Use CSS-like selectors to locate the elements
text_elements = pdf.pq('LTTextLineHorizontal')

# Extract the text from the elements
text = [t.text for t in text_elements]
thisdict={}
adict=[]
row = 0
temp=[]
for t in text:
    if "Phone/Cell:" in t:
        t = t.replace("Phone/Cell: ", "")
        temp.append(t)

for t in text:
    if "Phone/Cell:" in t:
        t = t.replace("Phone/Cell:", "")
        thisdict["Notes"] = t
    if "Office:" in t:
        t = t.replace("Office:", "")
        thisdict["Office"] = t
    if "Phone/Fax:" in t:
        t = t.replace("Phone/Fax:", "")
        thisdict["Mobile Phone"] = t
    if "Email:" in t:
        t = t.replace("Email:", "")
        thisdict["Email"] = t
    if "Contact:" in t:
        t = t.replace('Contact:', "")
        thisdict["Contact"] = t
    if "Contact Phone:" in t:
        t = t.replace('Contact Phone:', "")
        thisdict["Phone"] =t
        adict.append(thisdict.copy())
        thisdict={}
pprint(adict)

with open("pdf_output.csv", 'w', newline='\n') as file:
    fieldnames = ["Contact", "Email", "Phone", "Mobile Phone", "Notes"]
    wright = csv.DictWriter(file, fieldnames=fieldnames)
    wright.writeheader() 
    for li in adict:
        wright.writerow({
        "Contact": li["Contact"],
        "Email": li["Email"],
        "Phone": li["Phone"],
        "Mobile Phone": li["Notes"],
        "Notes":li["Mobile Phone"] + ",\n" + "Office:" + li["Office"]
        })