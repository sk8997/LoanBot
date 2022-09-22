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


# %% 
"""
0) Importing relevant libraries and setting global  variables

"""



import typing 
import numpy as np
import pandas as pd

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
    





