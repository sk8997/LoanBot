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
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler, OrdinalEncoder
from sklearn.decomposition import PCA
from matplotlib.ticker import PercentFormatter

# Global values
file_name: str = "credit_risk_dataset.csv" # Name of the dataset
seed: int = 4634     # Seed for the random state in Test/Train split
num_trees: int = 1000  # How many trees are used for the Random Forest 
test_proportion: float = 0.3  # Proportion of the test set for Test/Train split
kaiser_threshold: int = 1 # Threshold for the Kaiser criterion used to choose relevant Eigenvalues
variance_threshold: float = 1.00 # Threshold for the n% criterion used to choose relevant Eigenvalues. 100% by default

# Flags
ridge: bool = True # Flag for the type of ML model. True for Rindge Regression, False for Random Forest.
kaiser: bool = False # Flag for the type of Eigenvalue selection. Either Kaiser or n%.
save_as_sav: bool = True # Save model as a .sav file 


# TODO os, descriptives dataframe, report

# %%


"""
1) Loading the dataset 


"""

# Loading dataset
risk_data: pd.DataFrame = pd.read_csv(file_name)

# Check first 10 rows

risk_data.sample(10)
initial_row_num: int = risk_data.shape[0]
num_columns = len(risk_data.columns)


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

   * Drop redundant columns ("cb_person_cred_hist_length", "loan_int_rate", "loan_percent_income", "loan_intent")
   * Replace missing values for the employ. length column with mode
   * Change personal income to binary (above $50K/year or below $50K/year)
   * Change employement legth to binary (employed/unemployed; employed if employement length > 0)

"""

# %%

"""
a) Drop redundant columns ("cb_person_cred_hist_length", "loan_int_rate", "loan_intent")

"""
# Drop
risk_data.drop(["cb_person_cred_hist_length", "loan_int_rate", "loan_percent_income","loan_intent"], axis = 1, inplace = True)

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

# Rename columns for deployement 

risk_data.rename(columns={"person_age": "age", "person_income": "income", "person_emp_length": "employed", "loan_amnt": "loan_amount"})

# Replace

risk_data["person_emp_length"] = np.where(risk_data["person_emp_length"] > 0, "employed", "unemployed")


# Separate predictor and outcome variables 
X = risk_data.drop("loan_status", inplace = False, axis = 1)
Y = risk_data["loan_status"]

num_predictor_columns = len(X.columns) # How many predictor values left after cleaning. Will need this later for the PCA



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
Will use Kaiser criterion or n% of the variance explained to select important Eigenvalues.

"""

if (ridge):
    
    categorical_cols = ["person_income", "person_home_ownership", "person_emp_length", "loan_grade", "cb_person_default_on_file"]
    # Change all values to numeric 
    encoder = OrdinalEncoder()
    X[categorical_cols] = encoder.fit_transform(X[categorical_cols])
    
    
    # Save ecnoder for deployment
    np.save('risk_encoder.npy', encoder.categories_)
    
    # Z score data to avoid (1) offset and (2) unequal variance
    #zscored_X = stats.zscore(X)
    
    # Apply the PCA
    
    pca = PCA().fit(X)
    
    # Save PCA
    filename = "risk_pca.sav"

    pickle.dump(pca.components_, open(filename, "wb"))
    pickle.dump(pca.mean_, open("risk_pca_mean.sav", "wb"))
    
    #Eigenvalues 
    eig_vals = pca.explained_variance_
    
    # Eigenvectors (where the principla components point in terms of the original variables)
    loadings = pca.components_
    
    # Transformed data. Original variables substituted with factors ordered in decreasing Eigenvalues
    rotated_data = pca.fit_transform(X)
    
    # Explained variance for each factor 
    
    var_explained = pca.explained_variance_ratio_ * 100
    
    # Get the number of Eigenvalues that are above or equal to Kaiser criterion
    def get_kaiser_number(eig_vals: np.array, kaiser_threshold: int) -> int:
        count: int = 0
        
        for eig_val in eig_vals:
            if (eig_val >= kaiser_threshold):
                count += 1
        return count
    
    # Get the number of Eigenvalues that are above or equal to n% criterion
    def get_n_percent_number(var_explained: np.array, variance_threshold: int) -> int:
        count: int = 1
        total_var: int = 0
        
        for eig_val in var_explained:
            total_var += eig_val
            
            if (total_var >= variance_threshold * 100):
                return count
            count += 1
            
        return count
        
            
        
    # How many principal components to select
    if (kaiser):
        principal_comp_num: int = get_kaiser_number(eig_vals, kaiser_threshold)
    else:
        principal_comp_num: int = get_n_percent_number(var_explained, variance_threshold)
    
    
    # Scree plot (bar graph of the sorted Eigenvalues)
    dims = np.linspace(1, num_predictor_columns, num_predictor_columns)
    
    plt.bar(dims, eig_vals, color ="grey")
    plt.plot([0,num_predictor_columns],[kaiser_threshold,kaiser_threshold],color='orange')
    plt.xlabel('Principal component')
    plt.ylabel('Eigenvalue')

    plt.annotate("Selected " + str(principal_comp_num) + " Principal Components\nTotal variance explained is:\n" 
                 + str(round(sum(var_explained[range(0,principal_comp_num)]), 2)) + "%", xy = (3.3, 1.45), fontsize = 12)
    plt.show()
                 
        
    # Remove principal components that were not selected by the Kaiser/User criterion
    X_pca: np.array = rotated_data[:, 0 : principal_comp_num]
    
# %%

"""
a.2) Model 
    
Ridge Regression using selected principal components from part a.1)

Will use final classification results to asses model accuracy but we are interested 
in probabilities of defaulting

"""

if (ridge):
    
    # Test/train split
    X_train_pca, X_test_pca, y_train, y_test = train_test_split(X_pca, Y, 
                                                                test_size = test_proportion, 
                                                                random_state = seed, shuffle = True)
    
    # Fit the model
    clf = LogisticRegression().fit(X_train_pca, y_train)
    
    # Get probability for each prediction
    predictions_probability = clf.predict_proba(X_test_pca)

    # Make Predictions 
    predictions_final = clf.predict(X_test_pca)
    
    # Measure accuracy
    
    accuracy = accuracy_score(y_test, predictions_final)
    
    # Summary of the model
    print(classification_report(y_test, predictions_final))
    
    # Confusion matrix
    conf_matrix = confusion_matrix(y_test, predictions_final)
    sns.heatmap(conf_matrix)
    
    # AUC
    auc = roc_auc_score(y_test, predictions_final)
    
    
    average_probability = sum(predictions_probability[1]) / len(predictions_probability[1])


# %%

"""
Save this model as .sav

"""


if (save_as_sav):
    
    filename = "risk_model.sav"

    pickle.dump(clf, open(filename, "wb"))





