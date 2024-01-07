# importing libraries
from xml.etree import ElementTree
import os
import pandas as pd
from collections import Counter
from collections import defaultdict

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

# # saving as csv file
df.to_csv("cpdr.csv")

## calculating counts of the info ##

# list of column names
columns = df.columns.tolist()

# empty dataframe to store
dfInfo = pd.DataFrame()

# categories and sub categories for object type and material

material_dict = {
    'animal product': ['bone', 'ivory', 'leather', 'vellum', 'wool'],
    'bark': [],
    'ceramic': ['terracotta'],
    'fabric/cloth': ['canvas', 'Linen'],
    'gemstones': ['agate', 'diamond', 'turquoise'],
    'glass': [],
    'human remains': [],
    'ink or dye': [],
    'metal': ['brass', 'bronze', 'copper', 'gold', 'silver', 'steel'],
    'paint': ['fresco', 'oil', 'tempera', 'watercolor'],
    'paper': ['papier-mâché'],
    'plaster': [],
    'shell': [],
    'stone': ['alabaster', 'basalt', 'chlorite', 'fuschite', 'granodiorite', 'limestone', 'marble', 'sandstone', 'soapstone', 'tuff'],
    'wood': []
}

type_dict = {
    'Amphora': [],
    'Amulet': [],
    'Animal Skeleton': [],
    'Apparel': ['Belt'],
    'Armor': [],
    'Bead': [],
    'Bell': [],
    'Book': [],
    'Bronze': [],
    'Building': ['Column', 'Door', 'Strut', 'Window'],
    'Bust': [],
    'Candelabrum': [],
    'Carving': [],
    'Coffin': ['sarcophagus'],
    'Coin': [],
    'Cutlery': [],
    'Cylinder Seal': [],
    'Drawing': [],
    'Figurine': [],
    'Firearm': [],
    'Folio': [],
    'Food/Drink Container': ['Krater', 'Phiale'],
    'Funerary Object': [],
    'Furniture': ['Throne'],
    'Game': [],
    'Gemstone': [],
    'Human Remains': [],
    'Jewelry': ['Bracelet', 'Brooch', 'Ear ornament', 'Necklace'],
    'Manuscript': ['Letter(s)'],
    'Mask': [],
    'Mold': [],
    'Mosaic': [],
    'Music Score': ['Choirbook'],
    'Painting': [],
    'Panel': ['Fresco', 'Mural', 'Relief'],
    'Plaque or Tablet': [],
    'Print': ['Monotype'],
    'Relic': [],
    'Relief': [],
    'Religious Icon': [],
    'Sculpture': ['Casting'],
    'Seal': [],
    'Shield': [],
    'Sphinx': [],
    'Statue': [],
    'Stele': [],
    'Storage container': ['Pithos'],
    'Textile': [],
    'Timepiece': [],
    'Tombstone': [],
    'Tool': [],
    'Totem Pole': [],
    'Vase': [],
    'Vessel': [],
    'Weapon': ['Axe', 'Spearhead'],
    'Weight': []
}

print(columns)



# iterating through columns
for i in columns:
    if i == "cpdr_object_type" or i == "cpdr_object_material":
        # your code goes here
        print("hi")
        for j in df[i]:
            print(j)
        newDf = df[i].value_counts().to_frame()
    # else:
    #     newDf = df[i].value_counts().to_frame()
        newDf.to_csv(i + ".csv")
        dfInfo = pd.concat([dfInfo, newDf], axis=0)

print(dfInfo)

dfInfo.to_csv("cpdrcount.csv")