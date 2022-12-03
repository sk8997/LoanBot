
import requests
import discord
import regex as re
import os
import json
import pdfbox
from requests.compat import urljoin
from dotenv import load_dotenv
from discord.ext import commands
from loan_user import *
from application_parser import *


class LoanBot(commands.Bot):
    """Class for a discord bot that communicates with users and collects their data.  

    Extends:
        Bot (discord.ext.command)
    """

    users: list = []
            

    def __init__(self) -> None:
        """Contructor for the LoanBot. All commands are prefixed with '/'
        """
        super().__init__(command_prefix = "/", intents = discord.Intents.all())


        self.setup() # Notify when ready
        self.add_commands() # Define commands
        
    
    def setup(self) -> None:
        """Start the bot. Prints message to the console when bot is ready
        """
        @self.listen()
        async def on_ready() -> None:
            print("Bot is now online")

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
            usr.update_stage() # Proceed to next stage

    async def get_stage_one(self, message: discord.Message, usr: LoanUser) -> None:
        """Interaction for the first stage. Get intended loan amount and send user empty application to submit

        Args:
            message (discord.Message): message received from the user
            usr (LoanUser): current user object
        """
        if message.content.isnumeric():  # Check if user gave a number. Loan amount must be numeric

                usr.push_to_df(["loan_amount"], [message.content])  # Push this amount to the dataframe 
                await message.channel.send(f"Wonderful!! We will be looking for a ${message.content} loan\nPlease, fill out the attached document and send it back to me as a .pdf file")
                await message.channel.send(file = discord.File("LoanApplicationExample.docx"))

                usr.update_stage() # proceed to next stage
        else:
            await message.channel.send("Sorry, I don't think this is a valid amount. Please make sure that you enter a valid number without '$'")
    
    async def get_stage_two(self, message: discord.Message, usr: LoanUser) -> None:

        if len(message.attachments) != 1 or not (file_name := message.attachments[0].filename).endswith(".pdf"):
            return

        await message.attachments[0].save(file_name)
        
        parser = LoanApplicationParser(file_name)
        text = parser.get_text()

        print(text)
        os.remove(file_name)


        
        



    
    async def respond_to_user(self, message: discord.Message, usr: LoanUser) -> None:
        """Main logic of bot-user interaction. This function handles all interactions with user. This process is staged, such that each stage involves a separate set of interactions. This function is using elif statements to avoid incompatibility with python versions below 3.10 

        Args:
            message (Message): message that has been received from the user
            usr (LoanUser): Current user object
        See:
            init_user()
        """

        stage = usr.stage
        
        if (stage == 0):  # Get name

            await self.get_stage_zero(message, usr)

        elif (stage == 1):   # Get loan amount and send empty pdf
            
            await self.get_stage_one(message, usr)
        
        elif (stage == 2):

            await self.get_stage_two(message, usr)

                    
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

    

    


    




