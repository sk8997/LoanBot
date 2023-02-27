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
# TODO add link to Kaggle dataset

# %% 
"""
0) Importing relevant libraries and set global variables

"""

import re
import pickle
import typing 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder



# Global Variables 
data_name: str = "salary.csv" # name of the dataset
seed: int = 4634  # random state for train/test split
num_trees: int = 1000 # number of trees for boosting  
test_proportion: float = 0.3 # Proportion of the test set for Test/Train split


# Flags

save_as_sav: bool = False


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
    * Remove redundant dimnesions (fnlwgt, education-num, relationship, capital-loss/gain)
    * Reduce marital-status to binary outcomes (married, not married)
    * Replace native-country value with "developing" and "developed"
    * Convert outcome varibale "salary" to numeric binary values (1, 0)
    * Change education values with grade numbers to "Some-HS"

"""

# Check for missing values

salary_data.isnull().values.any()



# No NaN's, but quick visual inspection of the dataframe shown that there are some
# rows with "?" when no entries are avaliable for this unit. So we will replace them with the most common value in each respective column

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
Removing redundant dimensions (fnlwgt, education-num, relationship, capital-loss, capital-gain)

"""

salary_data.drop(["education-num", "fnlwgt", "relationship", "capital-loss", "capital-gain"], axis = 1, inplace = True)
    
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

developed_countries: list = pd.read_csv("HDI.csv")

developed_countries = developed_countries[developed_countries["hdi2019"] >= 0.8] # Drop developing countries
developed_countries = (developed_countries["country"]).tolist() # Get a list of only developed countries

# Match the spelling style in both datasets
salary_data["native-country"] = salary_data["native-country"].str.strip() # remove white spaces


for country in range(0, len(developed_countries)):
    developed_countries[country] = developed_countries[country].replace(" ", "-") # Repalce space between words in a country name with a "-"
    

# Replace native-country values 

salary_data["native-country"] = np.where(salary_data["native-country"].isin(developed_countries), "developed", "developing")

# %%

"""
Remove spaces from categorical columns 
"""

salary_data = salary_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)



# %%

"""
Change education values with grade numbers to "Some-HS" and Rename native-country


"""
salary_data["education"] = salary_data["education"].str.replace(r'[0-9]+th', "Some-HS", regex = True) # replace with regex

salary_data = salary_data.rename(columns = {"native-country": "native_country"})

# %%

"""
4) Fit the model
    
"""

# Separate predictor and outcome varibales

X = salary_data.drop("salary", axis = 1, inplace=False)
Y = salary_data["salary"]

# Change categorical values 
encoder = OrdinalEncoder()
X[["workclass", "education", "occupation", "race", "sex", "native_country"]] = encoder.fit_transform(X[["workclass", "education", "occupation", "race", "sex", "native_country"]])
salary_data.sample(10)

# Save ecnoder for deployment
np.save('salary_encoder.npy', encoder.categories_)


# Split predictor and outcome into test and train subsets (70/30)



X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = test_proportion, random_state = seed)

# Fitting the model 


clf = RandomForestClassifier(n_estimators = num_trees).fit(X_train,y_train) #bagging 10,000 trees

# Predict outcomes and calculate the accuracy score

predictions = clf.predict(X_test) # Predicted Y
accuracy = accuracy_score(y_test, predictions) # Accuracy of the model 

# Print summary of the model 

print(classification_report(y_test, predictions))

# plot predicted vs actual outcomes (confusion matrix) 

conf_matrix = confusion_matrix(y_test, predictions)
sns.heatmap(conf_matrix)


# Save the model  as .sav

if (save_as_sav):
    filename = "salary_model.sav"
    
    pickle.dump(clf, open(filename, "wb"))


# %%

"""
Calculate Area Under the Curve (AUC)

"""

auc = roc_auc_score(y_test, predictions)




# %%

"""
5) Report

    
    
...




Random forest calssification shows good results. The reported precision and recall
are 61% and 60% respectively. The correspoding F1 score is 0.63 and the total
accuracy is 0.84. Given that this dataset was unbalansed these results can be 
considered satisfactory. The 84% accuracy also suggests that the model is
unbiased. Confusion matrix shows that both false positive and false negative 
rates are extrimely low. Please note that low frequency of correct prediction 
on the CM heatmap is also due to the fact that the dataset is unbalannced. Overall
the model shows satisfactory performance.

Other considerations: As shown in EDA, a lion share of varibales are unbalansed 
this will likely make the model less accurate for low-occuring values in the 
training set. Moreover, the mode of the capital-gains varibale is zero and this
data is not readily avalobale in a real-world applications.  
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
"""

