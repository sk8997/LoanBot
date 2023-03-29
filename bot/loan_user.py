import pandas as pd
from bot.loan_database import *

class Person(object):
    """
    Parent class for the 'User' class. 
    
    """

    person_number: int = 0 # How many unique users are instantiated


    def __init__(self, name: str, age: int) -> None:
        """Instantiate User Object with basic demographic data

        Args:
            name (str): name of the user
            age (int): age of the user
            gender (str): biological gender of the user. M/F
            race (str): race of the user
        """

        self.name = name
        self.age = age

        Person.person_number += 1


class LoanUser(Person):
    """
    This class holds key user data. It genarates unique user ID and stores a connection of user to the relevant entry in database.

    Extends:
        Person (class)

    """

    __column_names: list = [
            "id", "name", "age", "sex", "employed", "workclass", "education",
            "marrital_status", "occupation", "race", "hours_per_week", "native_country",
            "income", "person_home_ownership", "loan_grade", "loan_amount",
            "cb_person_default_on_file", "loan_status", "interest_rate", "notes"
            ]


    def __init__(self, name: str = None, age: int = None) -> None:
        super().__init__(name, age)

        # Create user dataframe
        self.__generate_user_dataframe()
        self.data = {}
        

        # Assign name and age to dataframe
        (self.user_data).loc[0, "name"] = self.name
        (self.user_data).loc[0, "age"] = self.age

        # Set interaction stage to zero. See more...

        self.stage: int = 0


    def __default_user(self):
        """Instantiate user with default data values.
        """
        (self.user_data).loc[0] = ["123234", "John", 23, "Male", "employed", "Private", "HS-grad", 0, "Sales", "White", "12","Peru", "1", "RENT", "C", 444, "N", None, None, None]


    def is_valid_age(age: int) -> bool:
        """Check is the age is within acceptable range

        Args:
            age (int): Age of the person

        Returns:
            bool: true if age is within acceptable range. False otherwise
        """
        try:
            valid = 130 >= age >= 0
        except ValueError:
            return False
        return valid

    def __generate_user_dataframe(self) -> None:
        """
        Create an empty pandas dataframe associated with this user

        """
        self.user_data = pd.DataFrame(columns = LoanUser.__column_names)

    def update_stage(self) -> None:
        """Proceeds to the next stage of user interaction with LoanBot
        """
        self.stage += 1
        

    def __is_in_table(self, db: LoanDatabase) -> bool:
        """Determines whether an entry already exists for this user. Checks for unique user id in loan table

        Args:
            db (LoanDatabase): loan database object

        Returns:
            bool: True if entry for this user already exists in this database. False otherwise
        """
        try:
            result = (db.read_query(f"SELECT count(*) FROM {LoanDatabase.table_name} WHERE id = '{self.user_id}'"))[0][0] != 0
            return result
        except mysql.connector.Error:
            return False

    def push_to_df(self, col_names: list, values: list) -> None:
        """Copy specified values from LoanUser object to designated pandas DataFrame. Value index must correspond to the index of column name. 

        Args:
            col_names (list): A list of column names to which add values. Must be names of the columns. See LoanUser._generate_user_dataframe()
            values (list): A list of value which will be added to the dataframe
        """

        for col in col_names:
            (self.user_data).loc[0, col] = values[col_names.index(col)]


    def dump_data_to_sql(self, db: LoanDatabase) -> int:
        """Upload user dataframe to MySQL Server. Uploads entire data that has been collected from the user. 
        This method will replace any data if previously inserted with new values. To insert specific
        values use: .update_user_data() method instead.

        Args:
            db (LoanDatabase): Database object connected MySQL Server

        Returns:
            int: 1 if data has been uploaded successfully; 0 otherwise
        """
             
        if (not self.__is_in_table(db)):

            try:
                self.user_data.to_sql(con = db.engine, name = LoanDatabase.table_name, if_exists = 'append')
            except sqlalchemy.exc.SQLAlchemyError:
                    return 0
            return 1

        else:
            try:
                db.execute_query(f"DELETE FROM {LoanDatabase.table_name} WHERE id = '{self.user_id}'")
                self.dump_data_to_sql(db)
            except mysql.connector.Error:
                return 0
    
    def get_user_data(self, db: LoanDatabase) -> pd.DataFrame:
        """Read data of this user from your MySQL Server.

        Args:
            db (LoanDatabase): Database object connected MySQL Server

        Returns:
            pd.DataFrame: Pandas dataframe with user data fetched from MySQL Server or None if user doesn't exist
        """

        try:
             sql_user = pd.read_sql_query(f"SELECT * FROM {LoanDatabase.table_name} WHERE id = '{self.user_id}'", con = db.connection)
             if sql_user.empty:
                raise ValueError("No data found for this user")
             user_data = pd.DataFrame(sql_user, columns = LoanUser.__column_names)
        except (pd.errors.DatabaseError, pd.errors.ProgrammingError): # Database issues
            user_data = None
        except (ValueError):  # No user data
            user_data = None

        return user_data

