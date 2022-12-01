
import requests
import discord
import os
import json
from requests.compat import urljoin
from dotenv import load_dotenv
from discord.ext import commands
from loan_user import *


class LoanBot(commands.Bot):

    users: list = []
            

    def __init__(self) -> None:
        super().__init__(command_prefix = "/", intents = discord.Intents.all())


        self.setup()
        self.add_commands()
        
    
    def setup(self) -> None:
        @self.listen()
        async def on_ready() -> None:
            print("Bot is now online")

    
    async def respond_to_user(self, message, usr: LoanUser):

        stage = usr.stage
        
        if (stage == 0):
            if message.content.startswith("Yes"):
                await message.channel.send("Perfect! I'll create an account on your name right away!\nAll done!\nNow, may I plase ask what loan amount are you expecting to receive?")
                usr.stage += 1

                self.respond_to_user(message, usr)
            else:
                await message.channel.send("What is your name then?")
        elif (stage == 1):
            usr.user_data["loan_amount"] = message.content
            if message.content.isnumeric():
                await message.channel.send("Wonderful!!\nPlease, fill out the attached document and send it back to me as a .pdf file")

                usr.stage += 1

                    
    def init_user(self, ctx, usr: LoanUser):

        @self.listen()
        async def on_message(message):
            if message.author == self.user:
                return
            else:
                await self.respond_to_user(message, usr)

    def add_commands(self) -> None:

        @self.command(name = "apply")
        async def apply(ctx):
            
            user = LoanUser(ctx.author.display_name, 18)

            await ctx.channel.send(f"Hello, thank you for choosing our services. Before we proceed, may I confrim that your name is {ctx.author.display_name}?")
            self.init_user(ctx, user)

    


    




