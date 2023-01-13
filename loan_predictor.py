import numpy as np
import pandas as pd
import pickle
from typing import Union, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA

class LoanPredictor(object):

    def __init__(self, data: pd.DataFrame) -> None:
        
        self.data = data

        # Final Results for both ML models
        self.predicted_salary = None
        self.chance_of_default = None

        # Default names for ML models
        self.salary_model_name = "salary_model.sav"
        self.risk_model_name = "risk_model.sav"

    def __load_model(self, file_name: str) -> Union[RandomForestClassifier, LogisticRegression]:

        return pickle.load(open(file_name, "rb"))


    def __separate_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, None]:

        try:
            salary_data = (self.data)[["age", "workclass", "education", "marital_status", "occupation", "race", "sex", "hours_per_week", "native_country"]]
            risk_data = (self.data)[["age", "income", "person_home_ownership", "employed", "loan_grade", "loan_amount", "cb_person_default_on_file"]]
        except:
            return None

        return salary_data, risk_data


    def __change_country_to_binary(self) -> None:

        developed_countries: list = pd.read_csv("C:\Projects\Salary_Prediction\HDI.csv")
        developed_countries = developed_countries[developed_countries["hdi2019"] >= 0.8] # Drop developing countries
        developed_countries = (developed_countries["country"]).tolist() # Get a list of only developed countries

        if self.data.loc[0, "native_country"] in developed_countries:
            self.data.loc[0, "native_country"] = "developed"
        else:
            self.data.loc[0, "native_country"] = "developing"

    def __clean_data(self) -> None:

        self.__change_country_to_binary()

        salary_data, risk_data = self.__separate_data()

        

    
