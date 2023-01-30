import numpy as np
import pandas as pd
import pickle
from scipy import stats
from loan_user import LoanUser 
from typing import Union, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA

class LoanPredictor(object):

    # Default names for ML models
    salary_model_filename: str = "salary_model.sav"
    risk_model_filename: str = "risk_model.sav"

    def __init__(self, usr: LoanUser) -> None:
        
        self.usr = usr

        # Final Results for both ML models
        self.predicted_salary = None
        self.chance_of_default = None

        self.__clean_data()

    def __load_model(self, file_name: str) -> Union[RandomForestClassifier, LogisticRegression]:

        return pickle.load(open(file_name, "rb"))


    def __separate_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, None]:

        try:
            salary_data = ((self.usr).user_data)[["age", "workclass", "education", "marrital_status", "occupation", "race", "sex", "hours_per_week", "native_country"]]
        except:
            return None
        
        return salary_data


    def __change_country_to_binary(self) -> None:

        developed_countries: list = pd.read_csv("C:\Projects\Salary_Prediction\HDI.csv")
        developed_countries = developed_countries[developed_countries["hdi2019"] >= 0.8] # Drop developing countries
        developed_countries = (developed_countries["country"]).tolist() # Get a list of only developed countries

        if self.usr.user_data.loc[0, "native_country"] in developed_countries:
            self.usr.user_data.loc[0, "native_country"] = "developed"
        else:
            self.usr.user_data.loc[0, "native_country"] = "developing"

    def __clean_data(self) -> None:

        self.__change_country_to_binary()

        self.salary_data = self.__separate_data()

    def __predict_salary(self) -> None:

        loaded_model = self.__load_model(self.salary_model_filename)

        salary = (self.salary_data).apply(LabelEncoder().fit_transform)

        # Predict
        predicted_income = loaded_model.predict(salary)

        # Push to df

        self.usr.push_to_df(["income", [predicted_income]])

    def __predict_risk(self) -> float:

        # Predict salary

        self.__predict_salary()

        # Extract risk model columns
        risk_data = (self.data)[["age", "income", "person_home_ownership", "employed", "loan_grade", "loan_amount", "cb_person_default_on_file"]]

        # PCA 
        risk_data = risk_data.apply(LabelEncoder().fit_transform)

        zscored = stats.zscore(risk_data)

        pca = PCA().fit(zscored)

        rotated_data = pca.fit_transform(zscored)

        # Load Model
        loaded_model = self.__load_model(self.risk_model_filename)

        # Predict 
        predicted_risk = loaded_model.predict(rotated_data)

        return predicted_risk



        



        

    
