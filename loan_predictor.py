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
    """Predicts loan interest rate
    """

    # Default names for ML models
    salary_model_filename: str = "salary_model.sav"
    risk_model_filename: str = "risk_model.sav"

    # Encoders
    risk_encoder: str = "risk_encoder.npy"
    salary_encoder: str = "salary_encoder.npy"

    def __init__(self, usr: LoanUser) -> None:
        """Default constructor for the predictor

        Args:
            usr (LoanUser): current user
        """
        
        self.usr = usr

        # Final Results for both ML models
        self.predicted_salary = None
        self.chance_of_default = None

        self.__clean_data()

    def __load_model(self, file_name: str) -> object:
        """Loads ML model from a file

        Args:
            file_name (str): name of the file

        Returns:
            object: any object that has been saved in a given file. For this particular project, this method used to load categories_ and mean_ object for ML models  
        """

        return pickle.load(open(file_name, "rb"))


    def __separate_data(self) -> Tuple[pd.DataFrame, None]:
        """Separates entire user dataframe into feature subset relevant to salary prediction model
        Returns:
            Tuple[pd.DataFrame, None]: returns either a dataframe with features relevant for salary prediction model or None if fails tp slice user data
        """

        try:
            salary_data = ((self.usr).user_data)[["age", "workclass", "education", "marrital_status", "occupation", "race", "sex", "hours_per_week", "native_country"]]
        except:
            return None
        
        return salary_data


    def __change_country_to_binary(self) -> None:
        """Preprocessing. Change native country to binary classification (developed, developing)
        """

        developed_countries: list = pd.read_csv("HDI.csv")
        developed_countries = developed_countries[developed_countries["hdi2019"] >= 0.8] # Drop developing countries
        developed_countries = (developed_countries["country"]).tolist() # Get a list of only developed countries

        if self.usr.user_data.loc[0, "native_country"] in developed_countries:
            self.usr.user_data.loc[0, "native_country"] = "developed"
        else:
            self.usr.user_data.loc[0, "native_country"] = "developing"

    def __clean_data(self) -> None:
        """Wrapper method. Perfoms all nessesary data cleaning operations 
        """

        self.__change_country_to_binary()

        self.salary_data = self.__separate_data()

    def __predict_salary(self) -> None:
        """Predicts whether user salary is above $50K a year and pushes results to dataframe
        """

        loaded_model = self.__load_model(self.salary_model_filename)
        

        encoder = OrdinalEncoder()
        encoder.categories_ = np.load(self.salary_encoder, allow_pickle = True)

        # Encode 
        self.salary_data[["workclass", "education", "occupation", "race", "sex", "native_country"]] = encoder.transform(self.salary_data[["workclass", "education", "occupation", "race", "sex", "native_country"]])
        
        # Predict
        predicted_income = loaded_model.predict(self.salary_data)


        if predicted_income == 0:
            self.usr.push_to_df(["income"], ["<=50K"])
        else:
            self.usr.push_to_df(["income"], [">50K"])

    def _predict_risk(self) -> float:
        """Predicts the likelyhood of defaulting on a loan

        Returns:
            float: likelyhood of defaulting on a loan for a given user [0, 1]
        """

        predicted_risk = None
        # Predict salary

        self.__predict_salary()

        # Extract risk model columns
        risk_data = ((self.usr).user_data)[["age", "income", "person_home_ownership", "employed", "loan_grade", "loan_amount", "cb_person_default_on_file"]]
        categorical_cols = ["income", "person_home_ownership", "employed", "loan_grade", "cb_person_default_on_file"]
        
        # PCA 

        # Load encoder 
        encoder = OrdinalEncoder()
        encoder.categories_ = np.load(self.risk_encoder, allow_pickle = True)

        risk_data[categorical_cols] = encoder.transform((risk_data[categorical_cols]).to_numpy().reshape(1, -1))

        #zscored = stats.zscore(risk_data)
        #print(zscored)

        pca = PCA()
        pca.components_ = self.__load_model("risk_pca.sav")
        pca.mean_ = self.__load_model("risk_pca_mean.sav")
        pca_data = pca.transform(risk_data)

        # Load Model
        loaded_model = self.__load_model(self.risk_model_filename)

        # Predict 
        predicted_risk = loaded_model.predict_proba(pca_data)

        return predicted_risk[0, 1]

    def __to_percent(self, interest: float, loan_amount: float) -> int:
        """Transform interest amount to percentage of original loan amount

        Args:
            interest (float): calculated interest amount
            loan_amount (float): original loan amount 

        Returns:
            int: interest rate (rounded down) 
        """
        return int((interest / loan_amount) * 100)



    def _get_interest_rate(self, theta_rate: float = 0, weight_normalization: float = 0) -> int:
        """Calculates interest rate from loan amount and risk of default. This function maximizes interest amount such that expected gain from loan is greater than some value theta. That is E[gain] > theta. 

        Args:
            theta_rate (float, optional): Percentage of original loan amount that is expected to be the minimul profit amount for the loan issuer. Must be between 0 and 1. Defaults to 0.
            weight_normalization (float, optional): Normalization value that decreases or increases the average default probability. The greater the value, the smaller interest rates will be. Must be between 0 and 1. Defaults to 0.

        Returns:
            int: final interest rate
        """
        if 0> theta_rate > 1:
            theta_rate = 0

        average_probability = 0.2181 * (1 - weight_normalization)
        individual_probability = self._predict_risk()

        weighted_probability = individual_probability * average_probability
        loan_amount = self.usr.user_data["loan_amount"].iloc[0]

        interest = ((theta_rate * loan_amount) + loan_amount * weighted_probability) / 1 - weighted_probability

        return self.__to_percent(interest, loan_amount)




        



        

    
