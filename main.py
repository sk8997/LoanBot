import configparser
import sys

from bot.loan_bot import LoanBot
from typing import Dict, Tuple


def main():

    config = configparser.ConfigParser()

    try:
        token, configs = get_configs(config)
    except configparser.NoOptionError:
        print("One of the keys does not exist. Please make sure that config.txt file retains its original lines")
        raise SystemExit(1)
    except ValueError as err:
        print(f"Please make sure to provide all nessesary configurations. Error: {err}")
        sys.exit(1)

    loan_bot = LoanBot(**configs)
    loan_bot.run(token)
    

def get_configs(parser: configparser.ConfigParser) -> Tuple[str, Dict[str, str]]:

    # Read the config file
    parser.read("config.txt")


    configs: dict = {
    'username': parser.get('database', 'username'),
    'hostname': parser.get('database', 'hostname'),
    'password': parser.get('database', 'password'),
    'token': parser.get('bot', 'token'),
    'normalization': parser.get('model', 'interest_normalization')}

    for value in configs.values():
        if not value:
            raise ValueError("One or more configurations are empty or None")
        
    token: str = configs.pop('token')
        
    return token, configs



main()