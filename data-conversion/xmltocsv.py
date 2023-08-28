# importing libraries
from xml.etree import ElementTree
import os
import pandas as pd

# finding spreadsheet
os.chdir("/Users/asawyer/Desktop/CS/Projects/cpdr-dataviz/data-conversion")
# input file
tree = ElementTree.parse("culturalpropertydisputesresource.WordPress.2023-05-11.xml")

# TODO: fix postmetas code
# to find postmetas
# from lxml import etree
# root = tree.getroot()
# rss = ElementTree.tostring(root, encoding='utf8', method='xml')
# doc = etree.XML(rss)
# ns = { (k if k else "xx"):(v) for k, v in doc.xpath('//namespace::*') }
# for time in doc.xpath("//wp:meta_key[.='_edit_last']/following-sibling::wp:meta_value/text()", namespaces=ns):
#    print(time)

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
        domain = i.attrib['domain']
        category_text = i.text
        
        if domain in featureDict:
            featureDict[domain].append(category_text)
        else:
            featureDict[domain] = [category_text]

    # adding item and it's library to the larger library
    itemDict[item] = featureDict


# making dataframe from dictionary as items
df = pd.DataFrame.from_dict(itemDict, orient="index")

## deleting bad cpdrs ##

# get list of all the items (column 1)
itemNames = df.index.values.tolist()

# finding getting list of the rows to be deleted
badItems = []
for i in itemNames:
    if "[" in i:
        badItems.append(i)

# delete all of those rows, iterate through rows 
df = df.drop(badItems)

print(df)
# # saving as csv file
df.to_csv("cpdr.csv")

# ## calculating counts of the info ##

# # list of column names
# columns = df.columns.tolist()

# # empty dataframe to store
# dfInfo = pd.DataFrame()

# # iterating through columns
# for i in columns:
#     newDf = df[i].value_counts().to_frame()
#     newDf.to_csv(i + ".csv")
#     dfInfo = pd.concat([dfInfo, newDf], axis=0)

# print(dfInfo)

# dfInfo.to_csv("cpdrcount.csv")