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


# # for postmetas
# from lxml import etree
# root = tree.getroot()
# rss = ElementTree.tostring(root, encoding='utf8', method='xml')
# doc = etree.XML(rss)
# ns = { (k if k else "xx"):(v) for k, v in doc.xpath('//namespace::*') }

#searching, for example, for "_payment_method"
#for company in doc.xpath("//wp:meta_key[.='_edit_last']/following-sibling::wp:meta_value/text()", namespaces=ns):
#    print(company)


root = tree.getroot()

# making a dictionary with items
itemDict = {}
for itemData in root.findall('.//item'):
    featureDict = {} # to store specific things about the item 

    # item title
    item = itemData.find('title').text 

    # getting info from categories  
    categories = itemData.findall('category')
    for i in categories:
        featureDict[i.attrib['domain']] = (i.text)

    itemDict[item] = featureDict

print(itemDict)
# done !
cpdrData.close()
