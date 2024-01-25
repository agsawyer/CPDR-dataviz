# importing libraries
from xml.etree import ElementTree
import os
import csv

# finding spreadsheet
os.chdir("/Users/aly/Desktop/CS/Projects/cpdr")
# input file
tree = ElementTree.parse("culturalpropertydisputesresource.WordPress.2023-05-11.xml")

# output file 
cpdrData = open("cpdr.csv", "w", newline='',encoding="utf-8")
csvwriter = csv.writer(cpdrData)

# column names
colNames = ["item","complainant_nation","provenience_nation",
             "respondent_nation_economy","complainant_nation_economy",
             "case_status", "respondent_type", "complainant_type",
             "means_of_resolution", "respondent_nation",
             "year_of_object_creation","year_claim_initiated",
             "year_claim_resolved", "complainant_name","respondent_name"]
csvwriter.writerow(colNames)

root = tree.getroot()

# extracting items
for itemData in root.findall('.//item'):
    itemRow = [] # to store items 

    # item title
    item = itemData.find('title').text 
    itemRow.append(item)

    # getting categories  
    categories = itemData.findall('category')
    for i in categories:
        itemRow.append(i.text)
        # TODO: if none set to blank

    # make row in csv
    csvwriter.writerow(itemRow)

# done !
cpdrData.close()


# make dictionary w object inside
# {
#   “object1”: {
#       “date”: “today”,
#       “who stole it”: “Britain lmao”
#   },
#   “object2”: {
#       “date”: “yesterday”,
#       “who stole it”: “also Britain lmao”
#   }
#}
