# -*- coding: utf-8 -*-
"""
Salary Prediction ML Model

@author Stanislav Kharchenko



Dataset Column Descriptions: 
    
age: continuous.
workclass: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked.
fnlwgt: continuous.
education: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool.
education-num: continuous.
marital-status: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse.
occupation: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces.
relationship: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried.
race: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black.
sex: Female, Male.
capital-gain: continuous.
capital-loss: continuous.
hours-per-week: continuous.
native-country: United-States, Cambodia, England, Puerto-Rico, Canada, Germany, Outlying-US(Guam-USVI-etc), India, Japan, Greece, South, China, Cuba, Iran, Honduras, Philippines, Italy, Poland, Jamaica, Vietnam, Mexico, Portugal, Ireland, France, Dominican-Republic, Laos, Ecuador, Taiwan, Haiti, Columbia, Hungary, Guatemala, Nicaragua, Scotland, Thailand, Yugoslavia, El-Salvador, Trinadad&Tobago, Peru, Hong, Holand-Netherlands.
salary: <=50K or >50K




"""

# TODO Use os to detect the filepath for all datasets and remove hardcoded paths

# %% 
"""
0) Importing relevant libraries and setting global  variables

"""



import typing 
import numpy as np
import pandas as pd
import re

data_name: str = "C:\Projects\Salary_Prediction\salary.csv"






# %%
"""
1) Loading the dataframe

"""



# Load Data
salary_data: pd.DataFrame = pd.read_csv(data_name)

# Check first 10 rows

salary_data.sample(10)
initial_rows: int = salary_data.shape[0]



# %%

"""
2) Cleaning Data
    
    * Replace missing values with the mode of each column
    * Remove redundant dimnesions (fnlwgt, education, relationship)
    * Reduce marital-status to binary outcomes (married, not married)
    * Replace native-country value with "developing" and "developed"
    * Convert outcome varibale "salary" to numeric binary values (1, 0)

"""

# Check for missing values

salary_data.isnull().values.any()



# No NaN's, but quick visual inspection of the dataframe shown that there are some
# rows with "?" when no entries are avaliable for this unit. So we will replace them with the most common value in respective column

"""
Replacing "?" 

"""

def replace_with_most_common(df: pd.DataFrame, value) -> None:
    columns: list = df.columns
    
    for col in columns:
        
        most_common_value = df[col].value_counts().idxmax() # most common value in this col
        df[col].replace(value, most_common_value, inplace = True) # replace given with the most common value 
                
replace_with_most_common(salary_data, ' ?') # Replace question marks with the most common value in each repective column 

# Check for question marks to make sure they are all gone
print(' ?' in salary_data.values) # Check if there are any question marks left in our dataframe. False if all question marks have been removed 


# %%

"""
Removing redundant dimensions (fnlwgt, education, relationship)

"""

salary_data.drop(["education", "fnlwgt", "relationship"], axis = 1, inplace = True)
    
# %%

"""
Reduce marital-status to binary outcomes (married, not married)
"""

# See all unique values in marital-status column

salary_data["marital-status"].value_counts()

# Married = 1, Single = 0

not_married_values: list = [" Divorced", " Never-married", " Widowed"]

# Replace categorical marital status values with descrete  
salary_data["marital-status"] = np.where(salary_data["marital-status"].isin(not_married_values), 0, 1)

# %%

"""
Convert outcome varibale "salary" to numeric binary values (1, 0)
"""

salary_data["salary"] = np.where(salary_data["salary"] == " >50K", 1, 0)

# %%

"""
Replace native-country value with "developing" and "developed"

Operationalize "developed" by the Human Development Index (HDI) released by the Human Development Report (https://hdr.undp.org/towards-hdr-2022)
HDI of 0.80 and above is classified as "developed".

HDI dataset taken from the World Population Review (https://worldpopulationreview.com/country-rankings/developed-countries)

"""

# Load HDI dataset

developed_countries: list = pd.read_csv("C:\Projects\Salary_Prediction\HDI.csv")

developed_countries = developed_countries[developed_countries["hdi2019"] >= 0.8] # Drop developing countries
developed_countries = (developed_countries["country"]).tolist() # Get a list of only developed countries

# Match the spelling style in both datasets
salary_data["native-country"] = salary_data["native-country"].str.strip() # remove white spaces


for country in range(0, len(developed_countries)):
    developed_countries[country] = developed_countries[country].replace(" ", "-") # Repalce space between words in a country name with a "-"
    

# Replace native-country values 

salary_data["native-country"] = np.where(salary_data["native-country"].isin(developed_countries), "developed", "developing")



