# -*- coding: utf-8 -*-
"""
Loan default preduction model

@author: Stanislav
"""

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
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from matplotlib.ticker import PercentFormatter


file_name: str = "credit_risk_dataset.csv" # Name of the dataset
seed: int = 4634     # Seed for the random state in Test/Train split
numTrees: int = 1000  # How many trees are used for the Random Forest 
test_proportion: float = 0.3  # Proportion of the test set for Test/Train split

# Flag for the type of ML model. True for Rindge Regression, False for Random Forest
ridge: bool = True

# %%


"""
1) Loading the dataset 


"""

# Loading dataset
risk_data: pd.DataFrame = pd.read_csv(file_name)

# Check first 10 rows

risk_data.sample(10)
initial_row_num: int = risk_data.shape[0]

"""
Test Train Split

"""

# Separate predictor and outcome variables 
X = risk_data.drop("loan_status", inplace = False, axis = 1)
Y = risk_data["loan_status"]

# Test/train split
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = test_proportion, random_state = seed, shuffle = True)


# %%


"""
 2) Exploratory Data Analysis 

"""

# Count missing vaslues 

missing_values = risk_data.isnull().sum()

# Only 2 columns with missing values: interest rate and emp. length.  Most missing values for the loan interest rate column.


# Descriptive statistics of the dataframe (Numerical columns only)

descriptives = risk_data.describe()

# Distribution of positive and negative outcomes (not defaulting or defaulting on loan)
# See whether the dataset is unbalansed 

sns.histplot(data = risk_data, x = "loan_status", stat = "probability", discrete = True, hue = "loan_status", shrink = 0.8 ).set(xticklabels = [])
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.xlabel("Defaulting On Loan (0 = No, 1 = Yes)")
plt.ylabel("Percentage")

# The dataset is unbalansed. Observations with loan default on file make up around 20% of the dataset.


# Check for multicollinearity/Correlation matrix

numeric_temp_risk_data = risk_data.apply(LabelEncoder().fit_transform)
sns.heatmap(numeric_temp_risk_data.corr(), annot = True)

# We can see that some values a highly correlated (like loan grade and previous default on file (0.54 cor coefficent))
# This suggests multicollinearity and can negatively influence the Logistic Regression Model.


# %%

"""
3) Cleaning Data

   * Drop redundant columns ("cb_person_cred_hist_length", "loan_int_rate", "loan_intent")
   * Replace missing values for the employ. length column with mode
   * Change personal income to binary (above $50K/year or below $50K/year)
   * Change employement legth to binary (employed/unemployed; employed if employement length > 0)

"""

# %%

"""
a) Drop redundant columns ("cb_person_cred_hist_length", "loan_int_rate", "loan_intent")

"""
# Drop
risk_data.drop(["cb_person_cred_hist_length", "loan_int_rate", "loan_intent"], axis = 1, inplace = True)

# %%

"""
b) Replace missing values for the employ. length column with mode

"""

# Replace
risk_data["person_emp_length"].fillna(risk_data["person_emp_length"].mode()[0], inplace = True)


# Check for missing values again

no_missing_values = risk_data.isna().sum().sum() == 0 # True if no NaNs present in this dataset

# %%

"""
c) Change personal income to binary (above $50K/year or below $50K/year)


"""

# Replace 

risk_data["person_income"] = np.where(risk_data["person_income"] > 50000, ">50K", "<=50K")


# %%

"""
d) Change employement legth to binary (employed/unemployed; employed if employement length > 0)

"""

# Replace

risk_data["person_emp_length"] = np.where(risk_data["person_emp_length"] > 0, "employed", "unemployed")





# %% 

"""
3) Fitting the Model
   a) Logistic Regression
   b) Random Forest 

"""

# %%

"""
a) Logistic Regression
   a.1) Principal Component Analysis (PCA)
   a.2) Model
   a.3) Summary

"""
# %%

"""
a.1) Dimensionality Reduction (PCA) 

Removes multicollinearity
Will use Kaiser criterion to select important Eigenvalues.

"""

if (ridge):
    
    
    # Change all values to numeric 
    X = X.apply(LabelEncoder().fit_transform)
    X.sample(10)
    
    # Z score data to avoid (1) offset and (2) unequal variance
    zscored_X = stats.zscore(X)
    
    # Apply the PCA
    
    pca = PCA().fit(zscored_X)
    
    #Eigenvalues 
    eig_vals = pca.explained_variance_
    
    # Eigenvectors (where the principla components point in terms of the original variables)
    loadings = pca.components_
    
    # Transformed data. Original variables substituted with factors ordered in decreasing Eigenvalues
    rotated_data = pca.fit_transform(zscored_X)
    
    # Explained variance for each factor 
    
    var_explained = eig_vals/sum(eig_vals)*100















