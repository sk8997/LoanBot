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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

file_name: str = "credit_risk_dataset.csv"
seed: int = 4634
numTrees: int = 1000




# %%


"""
1) Loading the dataset 


"""

# Loading dataset
risk_data: pd.DataFrame = pd.read_csv(file_name)

# Check first 10 rows

risk_data.sample(10)
initial_row_num: int = risk_data.shape[0]

# %%

"""
Cleaning Data

   * Replace missing values with mode
   * Drop redundant columns ("cb_person_cred_hist_length", "loan_int_rate", "loan_intent")
   * Change personal income to binary (above $50K/year or below $50K/year)
   * Change employement legth to binary (employed/unemployed; employed if employement length > 0)

"""








