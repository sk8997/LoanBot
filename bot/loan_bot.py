
import requests
import discord
import regex as re
import os
import json
import pdfbox
import itertools
from requests.compat import urljoin
from dotenv import load_dotenv
from discord.ext import commands
from bot.loan_user import *
from bot.application_parser import *
from bot.loan_predictor import *


class LoanBot(commands.Bot):
    """Class for a discord bot that communicates with users and collects their data.  

    Extends:
        Bot (discord.ext.command)
    """

    def __init__(self, username: str, hostname: str, password: str, normalization: float) -> None:
        """Main constructor for the Loan Bot. All commands are prefixed with '/'

        Args:
            username (str): MySQL username
            hostname (str): MySQL hostname
            password (str): MySQL password
            normalization (float): interest rate weight normalization
        """

        self.norm = normalization

        super().__init__(command_prefix = "/", intents = discord.Intents.all())


        self.setup() # Notify when ready
        self.add_commands() # Define commands
        self.__set_db(hostname, username, password) # Establish database connection
        
    
    def setup(self) -> None:
        """Start the bot. Prints message to the console when bot is ready
        """
        @self.listen()
        async def on_ready() -> None:
            print("Bot is now online")

    def _set_db(self, hostname, username, password) -> None:

        self.db_username = username
        self.db_hostname = hostname
        self.db_password = password

        self.db = LoanDatabase(self.db_username, self.db_hostname, self.db_password)

    @staticmethod
    def is_name(name: str) -> bool:
        """Checks whether a string corresponds to a name of an individual. Such names should not include most special characters such as ($,%,& etc) and numbers

        Args:
            name (str): Name to checked

        Returns:
            bool: true if this is a name of an individual, false otherwise
        """
        return re.match(r"^[\-'a-zA-Z ]+$", name) is not None

    async def get_stage_zero(self, message: discord.Message, usr: LoanUser) -> None:
        """Interaction for the stage zero. Get name and id of the user.

        Args:
            message (discord.Message): _description_
            usr (LoanUser): _description_
        """
        gave_name = None

        if message.content.startswith("No"): # This is answer to Welcome message. See apply() function first
            await message.channel.send("What is your full name then?")
        elif message.content.startswith("Yes") or (gave_name := LoanBot.is_name(message.content)):

            if gave_name != None:
                usr.name = message.content
            else:
                usr.name = message.author.display_name

            usr.user_id = message.author.id
            usr.push_to_df(["name", "id"], [usr.name, usr.user_id]) # Push new data to df

            await message.channel.send(f"Perfect, {usr.name}! I'll create an account for you right away!\nAll done!\nNow, what loan amount are you planning to receive?")

            usr.push_to_df(["id", "name"], [usr.user_id, usr.name]) # Update user data with new information

            usr.update_stage() # Proceed to next stage

    async def get_stage_one(self, message: discord.Message, usr: LoanUser) -> None:
        """Interaction for the first stage. Get intended loan amount and send user empty application to submit

        Args:
            message (discord.Message): message received from the user
            usr (LoanUser): current user object
        """
        if message.content.isnumeric():  # Check if user gave a number. Loan amount must be numeric

                usr.push_to_df(["loan_amount"], [int(message.content)])  # Push this amount to the dataframe 
                await message.channel.send(f"Wonderful!! We will be looking for a ${message.content} loan\nPlease, fill out the attached document and send it back to me as a .pdf file")
                await message.channel.send(file = discord.File("LoanApplicationExample.docx"))

                usr.update_stage() # proceed to next stage
        else:
            await message.channel.send("Sorry, I don't think this is a valid amount. Please make sure that you enter a valid number without '$'")

    def _get_info_message(self, usr_data: dict) -> str:
        """Generates a string equivalent of a dictionary with user data in it

        Args:
            usr_data (dict): user data from parsing loan application

        Returns:
            str: string version of user data
        """

        result = ""
        columns: list = ["Gender", "Race", "Employed", "Workclass", "Occupation", "Hours Worked Per Week", "Married",
        "Owns a House", "Education", "Native Country", "Loan Grade", "Previously Defaulted"]

        for (col, value) in zip(columns, usr_data.values()):
            result += f"{col}: {value}\n"

        return result
    
    async def get_stage_two(self, message: discord.Message, usr: LoanUser) -> None:
        """Interaction for the second stage. Get attached application as a pdf file, extract relevant data from this application and ask for user confirmation

        Args:
            message (discord.Message): message received from a user
            usr (LoanUser): current user object
        """

        if len(message.attachments) != 1 or not (file_name := message.attachments[0].filename).endswith(".pdf"):
            return

        file_path = "apps/" + file_name
        try: 
            await message.attachments[0].save(file_path)
            
            parser = LoanApplicationParser(file_path)
            usr_data = parser.parse()
        except ValueError:
            await message.channel.send("Sorry, I couldn't parse some fields of your application. Please make sure to follow guidelines and resubmit your application")
        except discord.HTTPException:
            try:
                os.remove(file_path)
                await message.channel.send("Sorry, an error occured. Please try resubmit you application")
                await message.attachments[0].save(file_path)
                
                parser = LoanApplicationParser(file_path)
                usr_data = parser.parse()
            except ValueError:
                await message.channel.send("Sorry, I couldn't parse some fields of your application. Please make sure to follow guidelines and resubmit your application")

        usr_info = self.__get_info_message(usr_data)

        await message.channel.send(f"Splendid! Here is what I managed to learn from your application:\n\nName: {usr.name}\n{usr_info}\n\n\n Now, please provide us with your age")
        os.remove(file_path)

        usr.push_to_df(list(usr_data.keys()), list(usr_data.values())) # Update dataframe with new infromation
        print(usr.user_data)
        usr.update_stage()

    async def get_stage_three(self, message: discord.Message, usr: LoanUser) -> None:

        if message.content.isnumeric() and 0 < int(message.content) < 130:  # Check if user gave a right number. 

                usr.push_to_df(["age"], [int(message.content)])  # Push this amount to the dataframe 
                await message.channel.send("Got it! Now, give me a moment while I calculate your results...")

                predictor = LoanPredictor(usr)

                interest_rate = predictor._get_interest_rate(weight_normalization = self.norm)

                await message.channel.send(f"Your expected interest is: {interest_rate}")
                usr.push_to_df(["interest_rate"], [interest_rate]) # Push calculated interest rate to user dataframe

                usr.dump_data_to_sql(self.db)

                usr.update_stage() # proceed to next stage
        else:
            await message.channel.send("Sorry, I don't think this is a valid age. Try again")


    async def respond_to_user(self, message: discord.Message, usr: LoanUser) -> None:
        """Main logic of bot-user interaction. This function handles all interactions with user. This process is staged, such that each stage involves a separate set of interactions. This function is using elif statements to avoid incompatibility with python versions below 3.10 

        Args:
            message (Message): message that has been received from the user
            usr (LoanUser): Current user object
        See:
            init_user()
        """

        stage = usr.stage

        stage_mapping = {
            0: self.get_stage_zero,
            1: self.get_stage_one,
            2: self.get_stage_two,
            3: self.get_stage_three
        }

        if stage in stage_mapping:
            await stage_mapping[stage](message, usr)
        else:
            raise ValueError(f"Incorrect Stage Has Been Passed: Stage: {stage}")

              
    def init_user(self, usr: LoanUser) -> None:
        """A wrapper function for respond_to_user(). Listens for messages and ignores those messages that were sent by the bot itself. 

        Args:
            usr (LoanUser): Empty user object
        See:
            apply()
        """
        @self.listen()
        async def on_message(message: discord.Message):
            if message.author == self.user:
                return
            else:
                await self.respond_to_user(message, usr)

    def add_commands(self) -> None:
        """Define all "/" commands for this bot
        """

        @self.command(name = "apply")
        async def apply(ctx: discord.ext.commands.Context) -> None:
            """/apply command. Starting command that will initiate application process. This inckudes gathering infromation if no user data alredy exists, pushing data to the server and making loan predictions.

            Args:
                ctx (Context): context at which command has been called
            """
            
            user = LoanUser() # Create empty user object 

            await ctx.channel.send(f"Hello, thank you for choosing our services. Before we proceed, may I confrim that your full name is {ctx.author.display_name}?") # Welcome message
            self.init_user(user) # Gather user data


    

    


    




