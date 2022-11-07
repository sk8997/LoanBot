import mysql.connector
import pandas as pd
from mysql.connector import Error

class LoanDatabase(object):
    """
    Database object. Establishes connection to MySQL Server, creates database and executes all relevant queries

    """

    db_name = "loan" # Default name for the database

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
 
    def set_connection(self, db_name: str = None) -> None:
        """Establish connection to MySQL Server

        Args:
            db_name (str): Name of our database
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
            cursor = (self.connection).cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + LoanDatabase.db_name)
        except Error as err:
             raise Exception(f"Couldn't create database. Error: {err}")

    def execute_query(self, query: str) -> None:
        """Execute MySQL query. Used to interact with MySQL Community Server Database. 

        Args:
            query (str): SQL query to be executed 
        """

        try:
            cursor = (self.connection).cursor()
            cursor.execute(query)
            (self.connection).commit()
        except Error as err:
            raise Exception(f"Couldn't execute this query. Error: {err}")



