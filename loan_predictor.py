import numpy as np
import pandas as pd
import pickle
from scipy import stats
from loan_user import LoanUser 
from typing import Union, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler, OrdinalEncoder
from sklearn.decomposition import PCA

class LoanPredictor(object):

    # Default names for ML models
    salary_model_filename: str = "salary_model.sav"
    risk_model_filename: str = "risk_model.sav"

    # Encoders
    risk_encoder: str = "risk_encoder.npy"
    salary_encoder: str = "salary_encoder.npy"

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
        print(self.salary_data)

        encoder = OrdinalEncoder()
        encoder.categories_ = np.load(self.salary_encoder, allow_pickle = True)


        self.salary_data[["workclass", "education", "occupation", "race", "sex", "native_country"]] = encoder.transform(self.salary_data[["workclass", "education", "occupation", "race", "sex", "native_country"]])
        print(self.salary_data)
        # Predict
        predicted_income = loaded_model.predict(self.salary_data)


        if predicted_income == 0:
            self.usr.push_to_df(["income"], ["<=50K"])
        else:
            self.usr.push_to_df(["income"], [">50K"])

    def _predict_risk(self) -> float:

        predicted_risk = None
        # Predict salary

        self.__predict_salary()

        # Extract risk model columns
        risk_data = ((self.usr).user_data)[["age", "income", "person_home_ownership", "employed", "loan_grade", "loan_amount", "cb_person_default_on_file"]]
        print(risk_data)
        # PCA 

        # Load encoder 
        encoder = OrdinalEncoder()
        encoder.categories_ = np.load(self.risk_encoder, allow_pickle = True)

        risk_data = encoder.inverse_transform((risk_data).to_numpy().reshape(1, -1))

        zscored = stats.zscore(risk_data)
        print(zscored)

        pca = PCA().fit(zscored)

        rotated_data = pca.fit_transform(zscored)

        # Load Model
        loaded_model = self.__load_model(self.risk_model_filename)

        # Predict 
        predicted_risk = loaded_model.predict(rotated_data)

        return predicted_risk



        



        

    
