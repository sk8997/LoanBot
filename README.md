# Loan Bot

Welcome to the Loan Bot project! This project is aimed at streamlining the loan application process by developing a bot that can interact with users, collect information from uploaded PDF files, and store it in a MySQL database.

## Description

The Loan Bot project represents a significant improvement over conventional loan application methods. By utilizing machine learning models, this method outperforms traditional methods in accurately predicting user's risk of default on loan, leading to a more customized and reliable loan amount recommendation. This innovative approach has the potential to revolutionize the loan application process and enhance financial decision-making.

## Features

- Interactive chat interface to guide the user through the loan application process
- Custom interest rate on a loan
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

This model determines the most suitable interest rate by maximizing the expected gain, given by the expression $((1 - r) \beta + \alpha) - r \alpha$. Here, $r$ denotes the weighted probability of default, $\beta$ represents the interest rate, and $\alpha$ is the loan amount. The model ensures that $\beta \geq \frac{\alpha r}{1 - r}$. The individual probability of default $r$ is weighted with the average probability of default to account for the model's oversensitivity to $r$. The `interest_normalization parameter` in the `config.txt` file, which takes a value in the range of `(0, 1)`, determines the model's sensitivity and the ceiling for the interest rate value. A higher normalization rate leads to a less sensitive model. Please refer to the figure below to compare the impact of normalization on interest rates. Also note that selecting an appropriate weight normalization is a significant financial undertaking that falls squarely on the shoulders of the user. Opting for an overly conservative normalization may yield excessively high interest rates, potentially leading to reduced borrowing and an elevated likelihood of default on larger loan sums. Conversely, selecting a normalization value that is too liberal may result in negligible interest rates and diminished financial returns. Herein, you shall find the output of a simulation conducted under various normalization values, premised on certain client behavior assumptions, while default risk was derived from the Gamma K = 2, Mean = 0.07 distribution. 



<img src="https://user-images.githubusercontent.com/84877088/229012159-98e609dc-566b-43e6-8586-05ae72daf59d.png" width=90% height=90% align="center"  alt="alt text">

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






