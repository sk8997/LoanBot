import mysql.connector
import pandas as pd
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from mysql.connector import Error

class LoanDatabase(object):
    """
    Database object. Establishes connection to MySQL Server, creates database and executes all relevant queries

    """

    db_name: str = "loan_database" # Default name for the database
    table_name: str = "loan_table" # Default name for the table 

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

        # Establish first connection and create a database + engine
        self.set_connection()
        self.create_database()
        self.create_engine()

        # Set connection to newly created database
        self.set_connection(LoanDatabase.db_name) 
        
 
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
        except mysql.connector.Error as err:
            raise Exception(f"Couldn't connect to the server. Please make sure that local MySQL server is set up properly and all credentials are correct. Error: {err}")

    def create_database(self) -> None:
        """

        Create Database for this application with default name.

        """
        try:
            cursor = (self.connection).cursor(buffered = True)
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + LoanDatabase.db_name)
        except mysql.connector.Error as err:
             raise Exception(f"Couldn't create database. Error: {err}")

    def create_engine(self) -> None:
        """Create sqlalchemy connection engine. This method uses mysql as a dialect and pymysql as a driver. Please refer to sqlachemy Database URL format: dialect+driver://username:password@host:port/database.
        This method is used to establish pandas friendly connection to MySQL server databse. Please refer to .to_sql method in pandas library

        Raises:
            Exception: Value errors. Mostly if username/password/host are incorrect
        """

        params: str = f"mysql+pymysql://{self.user_name}:{self.password}@{self.host_name}/{LoanDatabase.db_name}"

        try:
            engine = create_engine(params)
            self.engine = engine
        except sqlalchemy.exc.OperationalError as ex:
            raise Exception(f"Couldn't create engine with parameters {params}: Error: {ex}")



    def execute_query(self, query: str) -> None:
        """Execute MySQL query. Used to interact with MySQL Community Server Database. 

        Args:
            query (str): SQL query to be executed 
        """

        try:
            cursor = (self.connection).cursor(buffered = True)
            cursor.execute(query)
            (self.connection).commit()
        except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.IntegrityError) as err:
            raise mysql.connector.Error(f"Couldn't execute this query '{query}'. Error: {err}")

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
        except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.IntegrityError) as err:
            raise mysql.connector.Error(f"Couldn't read query '{query}'from the table. Error: {err}")





