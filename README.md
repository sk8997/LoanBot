# Loan Bot

Welcome to the Loan Bot project! This project is aimed at streamlining the loan application process by developing a bot that can interact with users, collect information from uploaded PDF files, and store it in a MySQL database. The bot employs advanced machine learning algorithms to predict a user's salary and risk of default on loan, enabling the most suitable loan amount recommendation.

## Description

The Loan Bot project represents a significant improvement over conventional loan application methods. By utilizing machine learning models, this method outperforms traditional methods in accurately predicting user's isk of default on loan, leading to a more customized and reliable loan amount recommendation. This innovative approach has the potential to revolutionize the loan application process and enhance financial decision-making.

## Features

- Interactive chat interface to guide the user through the loan application process
- Custumized interest rate on a loan
- MySQL database for storing user information and loan recommendations
- Configurable sensitivity to default risk
- User-friendly and intuitive design
- Improved loan application process over traditional methods

## Installation

To install the Loan Bot, please follow these steps:

1. Clone the project repository

```git clone https://github.com/username/loan-bot.git```

2. Install the required packages

```pip install -r requirements.txt```

3. Configure the bot by filling in the necessary information in the `config.txt` file, including the MySQL database information and bot token.

4. Run the app

```python main.py```

## Configuring sensitivity 

This model finds the most apparopriate interest rate by maximizing expected gain given by $$((1 - r) * \beta + \alpha) - r * \alpha$$

## Usage

To use the Loan Bot, follow these steps:

1. Upload a PDF file containing your financial information and demographic information
2. Answer questions and provide additional information as prompted by the chat interface
3. The bot will and recommend the most suitable interest rate

## Contributing

We welcome contributions to the Loan Bot project! To contribute, please follow these steps:

1. Fork the project repository
2. Create a new branch for your feature or bug fix
3. Implement your changes
4. Submit a pull request

Please ensure that your contributions adhere to our coding standards and follow the guidelines for contributing.

## License

The Loan Bot project is licensed under the MIT license. Please see the `LICENSE` file for more details.


<img src="https://user-images.githubusercontent.com/84877088/227412371-b60f6c21-bbb7-4a1a-a3c7-83f142f14b30.png" width=45% height=45% align="right"  alt="alt text">







