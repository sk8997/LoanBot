import mysql.connector
import pandas as pd
from mysql.connector import Error

class LoanDatabase(object):
    """
    Database object. Establishes connection to MySQL Server, creates database and executes all relevant queries

    """

    db_name: str = "loan_database" # Default name for the database
    table_name: str = "loan" # Default name for the table 
    __table_values: str = """
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    age INT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    employed INT,
    workclass VARCHAR(40),
    education VARCHAR(40),
    marrital_status INT,
    occupation VARCHAR(60),
    race VARCHAR(20),
    hours_per_week INT,
    native_country INT,
    income INT,
    person_home_ownership VARCHAR(40),
    loan_grade VARCHAR(3),
    loan_amount INT,
    loan_percent_income FLOAT,
    cb_person_default_on_file INT,
    loan_status INT,
    notes VARCHAR(500)
    """ 

    def __init__(self, user_name: str, host_name: str, password: str) -> None:
        """Database constructor

        Args:
            user_name (str): Name of the user 
            host_name (str): Host name
            password (str): Password for the root access on a given MySQL Server
        """
        # Set Database values
        self.user_name = user_name
        self.host_name = host_name
        self.password = password

        # Establish first connection and create a database
        self.set_connection()
        self.create_database()

        # Create an empty table
        self.set_connection(LoanDatabase.db_name) 
        self.execute_query(f"CREATE TABLE IF NOT EXISTS {LoanDatabase.table_name} ({LoanDatabase.__table_values});")
 
    def set_connection(self, db_name: str = None) -> None:
        """Establish connection to MySQL Server

        Args:
            db_name (str): Database name. Use to establish connection directly to specific database
        """
        self.connection = None
        try: 
            self.connection = mysql.connector.connect(
                    user = self.user_name,
                    host = self.host_name,
                    password = self.password,
                    database = db_name
                )
        except Error as err:
            raise Exception(f"Couldn't connect to the server. Please make sure that local MySQL server is set up properly and all credentials are correct. Error: {err}")

    def create_database(self) -> None:
        """

        Create Database for this application with default name.

        """
        try:
            cursor = (self.connection).cursor(buffered = True)
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + LoanDatabase.db_name)
        except Error as err:
             raise Exception(f"Couldn't create database. Error: {err}")

    def execute_query(self, query: str) -> None:
        """Execute MySQL query. Used to interact with MySQL Community Server Database. 

        Args:
            query (str): SQL query to be executed 
        """

        try:
            cursor = (self.connection).cursor(buffered = True)
            cursor.execute(query)
            (self.connection).commit()
        except Error as err:
            raise Exception(f"Couldn't execute this query '{query}'. Error: {err}")

    def read_query(self, query: str) -> str:
        """Read from MySQL Server. Used to fetch data from the server 

        Args:
            query (str): MySQL query to be executed on a server

        Raises:
            Exception: For all instances when query execution failed. A more specific description of the error is given by mysql package

        Returns:
            str: Values returned by the Server after executing the query
        """

        try:
            cursor = (self.connection).cursor(buffered = True)
            cursor.execute(query)
            read = cursor.fetchall()

            return read
        except Error as err:
            raise Exception(f"Couldn't read query '{query}'from the table. Error: {err}")





