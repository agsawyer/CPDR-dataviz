from xml.etree import ElementTree
import os
import pandas as pd
from collections import Counter
from collections import defaultdict
import pycountry
import csv 

##############################################
## getting data from exported wordpress xml ## 
##############################################
country_coord = pd.read_csv('country-coord.csv')

# input file
tree = ElementTree.parse("culturalpropertydisputesresource.WordPress.2024-05-24.xml")

# TODO: fix postmetas code - it can't currently get postmeta data 
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

#############################
## deleting unusable cpdrs ##
#############################

# get list of all the items (column 1)
itemNames = df.index.values.tolist()

# remove NoneType
itemNames = [item for item in itemNames if item is not None]

# finding getting list of the rows to be deleted
badItems = []
for i in itemNames:
    if "[" in i:
        badItems.append(i)

# delete all of those rows, iterate through rows 
df = df.drop(badItems)

# convert list columns to strings
for column in df.columns:
    if isinstance(df[column][0], list):
        df[column] = df[column].apply(lambda x: str(x) if x is not None else None)
    
# saving as csv file
df.to_csv("cpdr.csv")

####################################
## calculating counts of the info ##
####################################

def get_country_code(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        return country.alpha_3
    except AttributeError:
        return None


# list of column names
columns = df.columns.tolist()

#################################
## getting country codes names ##
#################################

# making csv file for countries
countries = df["cpdr_respondent_nation"].tolist()
countries.append(df["cpdr_complainant_nation"].tolist())
new_countries = []
for country in countries:
    if country != "['2 or more respondent nations']" and type(country) != list:
        country = country.strip("[]").strip('\'\'')
        if country not in new_countries:
            new_countries.append(country) 

countries_and_codes = {}
country_coord = pd.read_csv('country-coord.csv')
for index, row in country_coord.iterrows():
    countries_and_codes[row['country']] = row['alpha3']


####################################
## generating csv file by country ##
####################################

# making csv file for categories
grouped_df = df.groupby('cpdr_respondent_nation')

dfs = []

def clean_string(s):
    """
    clean up a string with square brackets and quotes
    exp: "['Australia']" becomes "Australia"
    """
    s = s.strip("[]")  # Remove square brackets
    s = s.replace("'", "")  # Remove single quotes
    return s

# read in csv file from country-coord.csv and make a country, latitude, and longitude dictionary
country_coord = pd.read_csv('country-coord.csv')

country_dict = {}
reader = csv.reader(open('country-coord.csv', newline=''))
for row in reader:
    alpha3 = row[2]
    latitude = row[4]
    longitude = row[5]
    country_dict[alpha3] = [latitude, longitude]

# loop through each group
for name, group in grouped_df:
    # ignoring non individual countries 
    if name != "['2 or more respondent nations']" and name != "nan":
        try:
            # get country code, if possible
            code = countries_and_codes[clean_string(name)]

            # count total disputes
            count = group.shape[0]

            ##############################################
            #### find complainant  nation coordinates #### 
            ##############################################

            complainant_counts = group['cpdr_complainant_nation'].value_counts()

            country_names = complainant_counts.index.tolist()

            responses = group['cpdr_case_status'].tolist()

            current_complains = []

            # making a list of coordinates if there are complainants
            if count != 0:
                current_complains = [clean_string(country) for country in country_names]
                for index in range(len(current_complains)):
                    try:
                        current_code = countries_and_codes[current_complains[index]]
                        current_complains[index] = [country_dict[current_code][0], country_dict[current_code][1]] #TODO!!!
                    except Exception as e:
                        print(f"KeyError: {e}")
                        # Handle the KeyError here if needed
                current_complains = [x for x in current_complains if not isinstance(x, str)]

            # calculate result percentages
            # count occurrences of each unique response
            response_counts = {}
            for response in responses:
                if response in response_counts:
                    response_counts[response] += 1
                else:
                    response_counts[response] = 1

            # calculate percentage for each unique response
            total_responses = len(responses)
            percentage_distribution = {response: (count / total_responses) * 100 for response, count in response_counts.items()}

            # print results
            # Initialize an empty dictionary
            response_dict = {}

            response_dict["Object(s) relinquished"] = "N/A"
            # Populate the dictionary with response as key and percentage as value
            for response, percentage in percentage_distribution.items():
                if response == 'nan':
                    response = 'Unknown'
                response_dict[clean_string(response)] = f"{percentage:.2f}%"

            # aggregate the information, TODO: make more efficient 
                
            aggregated_info = {
                'name': clean_string(name),
                'code': code,
                'disputes': count,
                'complainant_nations': current_complains,
                'case_status': response_dict["Object(s) relinquished"],
                'latitude': country_dict[code][0],
                'longitude': country_dict[code][1]
            }
            
            # create a df for the aggregated information
            aggregated_df = pd.DataFrame([aggregated_info])
        
            # append the df to the list
            dfs.append(aggregated_df)
        except Exception as e:
            print(f"KeyError: {e}")


        

  
to_add = {}
# including rest of countries 
with open('all-countries.csv') as file_obj: 
      
    reader_obj = csv.reader(file_obj) 
      
    # iterate over each row in the csv file using reader object 
    for row in reader_obj: 
        if row[0] not in countries_and_codes:
            to_add[row[0]] = row[1]

# adding to output fle
for country, code in to_add.items():
    aggregated_info = {
        'name': country,
        'code': code,
        'disputes': 0,
        'complainant_nations': [],
        'case_status': 'N/A',
    }
    
    # aggregated information df
    aggregated_df = pd.DataFrame([aggregated_info])
    dfs.append(aggregated_df)

# concatenate all dfs
aggregated_df = pd.concat(dfs, ignore_index=True)

# save aggregated df
aggregated_df.to_csv('output_file.csv', index=False)