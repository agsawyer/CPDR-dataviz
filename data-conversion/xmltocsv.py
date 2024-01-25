from xml.etree import ElementTree
import os
import pandas as pd
from collections import Counter
from collections import defaultdict
import pycountry

##############################################
## getting data from exported wordpress xml ## 
##############################################

# input file
tree = ElementTree.parse("culturalpropertydisputesresource.WordPress.2023-05-11.xml")

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

# finding getting list of the rows to be deleted
badItems = []
for i in itemNames:
    if "[" in i:
        badItems.append(i)

# delete all of those rows, iterate through rows 
df = df.drop(badItems)

# Convert list columns to strings
for column in df.columns:
    if isinstance(df[column][0], list):
        df[column] = df[column].apply(lambda x: str(x) if x is not None else None)
    
# # saving as csv file
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

# TODO: find a better library that doesn't need this 
exceptions = {'Taiwan': 'TWN', 'South Korea': 'KOR', 'Syria': 'SYR', 'Bolivia': 'BOL', 'Russia': 'RUS', 'Australia': 'AUS'}

for country in new_countries:
    code = get_country_code(country)
    countries_and_codes[country] = code
    # exceptions 
    if country in exceptions: 
        countries_and_codes[country] = exceptions[country]

####################################
## generating csv file by country ##
####################################

# making csv file for categories
grouped_df = df.groupby('cpdr_respondent_nation')

dfs = []

def clean_string(s):
    """
    Clean up a string with square brackets and quotes.
    Example: "['Australia']" becomes "Australia".
    """
    s = s.strip("[]")  # Remove square brackets
    s = s.replace("'", "")  # Remove single quotes
    return s

# loop through each group
for name, group in grouped_df:
    if name != "['2 or more respondent nations']" and name != "nan":
        # count the occurrences of each nation
        count = group.shape[0]

        complainant_counts = group['cpdr_complainant_nation'].value_counts().to_dict()

        responses = group['cpdr_case_status'].tolist()

        complainant_counts = group['cpdr_complainant_nation'].value_counts().to_dict()
        cleaned_complainant_counts = {clean_string(k): v for k, v in complainant_counts.items()}

        
        # calculate result percentages
        # Count occurrences of each unique response
        response_counts = {}
        for response in responses:
            if response in response_counts:
                response_counts[response] += 1
            else:
                response_counts[response] = 1

        # Calculate percentage for each unique response
        total_responses = len(responses)
        percentage_distribution = {response: (count / total_responses) * 100 for response, count in response_counts.items()}

        # Print the results
        response_list = []
        for response, percentage in percentage_distribution.items():
            if response == 'nan':
                response = 'Unknown'
            response_list.append((f"{clean_string(response)}: {percentage:.2f}%"))

        print(response_list)
        # aggregate the information
        aggregated_info = {
            'name': clean_string(name),
            'code': countries_and_codes[clean_string(name)],
            'disputes': count,
            'complainant_nations': cleaned_complainant_counts,
            'case_status': response_list,
        }
        
        # Create a DataFrame for the aggregated information
        aggregated_df = pd.DataFrame([aggregated_info])
    
        # Append the DataFrame to the list
        dfs.append(aggregated_df)

# Concatenate all DataFrames in the list
aggregated_df = pd.concat(dfs, ignore_index=True)

# Save the aggregated DataFrame to a new CSV file
aggregated_df.to_csv('output_file.csv', index=False)

