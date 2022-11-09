import pandas as pd
from loan_database import *

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

    def __init__(self, name: str, age: int) -> None:
        super().__init__(name, age)

        # Create user dataframe
        self.generate_user_dataframe()
        self.get_id()

        # Assign name and age to dataframe
        self.user_data["id"] = self.user_id
        self.user_data["name"] = self.name
        self.user_data["age"] = self.age

    __column_names: list = [
        "id", "name", "age", "sex", "employed", "workclass", "education",
        "marrital_status", "occupation", "race", "hours_per_week", "native_country",
        "income", "person_home_ownership", "loan_grade", "loan_amount", "loan_percent_income",
        "cb_person_default_on_file", "loan_status", "notes"
        ]
    

    def get_id(self) -> None:
        """Generate a unique ID for the user. Note that this ID is not 'universaly' unique, meaning that uniqueness of this value is true only for local dataset
        """
        try:
            self.user_id: str = self.name[:4] + str(Person.person_number) + str(self.age)
        except:
            self.user_id: str = self.name[: len(self.name)] + str(Person.person_number) + str(self.age)

    def generate_user_dataframe(self) -> None:
        """
        Create an empty pandas dataframe associated with this user

        """
        self.user_data: pd.DataFrame = pd.DataFrame(columns = LoanUser.__column_names )

    def is_in_table(self, db: LoanDatabase) -> bool:
        """Determines whether an entry already exists for this user. Checks for unique user id in loan table

        Args:
            db (LoanDatabase): loan database object

        Returns:
            bool: True if entry for this user already exists in this database. False otherwise
        """
        result = (db.read_query(f"SELECT count(*) FROM {LoanDatabase.table_name} WHERE id = '{self.user_id}'"))[0][0] != 0
        return result

    def dump_data_to_sql(self, db: LoanDatabase) -> int:
        """Upload user dataframe to MySQL Server. Uploads entire data that has been collected from the user. 
        This method will replace any data if previously inserted with new values. To insert specific
        values use: .update_user_data() method instead.

        Args:
            db (LoanDatabase): Database object connected MySQL Server

        Returns:
            int: 1 if data has been uploaded successfully; 0 otherwise
        """
             
        if (not self.is_in_table(db)):

            try:
                self.user_data.to_sql(con = db.connection, name = LoanDatabase.db_name, if_exists = 'append')
            except Exception:
                try:
                    self.generate_user_dataframe()
                    self.user_data.to_sql(con = db.connection, name = LoanDatabase.db_name, if_exists = 'append')
                except Exception as ex:
                    print(f"Couldn't dump data: Error: '{ex}'")
                    return 0
            return 1

        else:
            db.execute_query(f"DELETE FROM {LoanDatabase.table_name} WHERE id = '{self.user_id}'")
            self.dump_data_to_sql(db)
    
    def get_user_data(self, db: LoanDatabase) -> pd.DataFrame:
        """Read data of this user from your MySQL Server.

        Args:
            db (LoanDatabase): Database object connected MySQL Server

        Returns:
            pd.DataFrame: Pandas dataframe with user data fetched from MySQL Server
        """

        sql_user = pd.read_sql_query(f"SELECT * FROM {LoanDatabase.db_name} WHERE id = {self.user_id}", con = db.connection)

        # Check if sql_user is empty to throw exception here

        try:
            user_data = pd.DataFrame(sql_user, columns = LoanUser.__column_names)
        except Exception:
            user_data = None

        return user_data

