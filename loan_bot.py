
import requests
import discord
import os
import json
from requests.compat import urljoin
from dotenv import load_dotenv
from discord.ext import commands


class LoanBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(command_prefix = "/", intents = discord.Intents.all())


        self.setup()
        self.add_commands()
        
    
    def setup(self) -> None:
        @self.listen()
        async def on_ready() -> None:
            print("Bot is now online")

        @self.listen()
        async def on_message(message) -> None:
            if message.author == self.user:
                return

            if message.content.startswith('Hello'):
                ms = "Hi, {0.author.mention}".format(message)
                await message.channel.send(ms)

    def add_commands(self) -> None:

        @self.command(name = "apply")
        async def apply(ctx):
            await ctx.channel.send(f"Hello, thank you for choosing our services...")

    




