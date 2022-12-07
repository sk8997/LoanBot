import pdfplumber
import re

class LoanApplicationParser(object):
    """Object for parsing loan applications
    """

    def __init__(self, file_name: str) -> None:
        """Construct a loan parser

        Args:
            file_name (str): Name of the application
        """
        
        self.file_name: str = file_name

        self.keys: list = ["sex", "race", "employed", "workclass", "occupation","hours_per_week", "marrital_status", "person_home_ownership", 
            "education", "native_country", "loan_grade", "cb_person_default_on_file"
            ]

    def get_text(self) -> str:
        """Extracts text from a pdf file

        Returns:
            str: string corresponding to a text of a given file or an empty string if file name was incorrerct or if no such file exists
        """

        text = ""

        try:
            pdf = pdfplumber.open(self.file_name)

            for page in pdf.pages:
                text += page.extract_text()
        except Exception:
            
            return ""
        finally:
            pdf.close()

        return text

    def __get_race_and_sex(self, data: dict, application: str) -> None:
        """Extract user race and gender from the pdf application

        Args:
            data (dict): dictionary to which the data extracted from pdf will be pushed
            application (str): string equivalent of user application. See .get_text()
        """

        # Find Race field and extract user answer
        race: str = re.findall("Race:\s*[a-zA-Z]*\s*\n*", application)[0]
        race = race.replace("Race: ", "")

        data["race"] = race.strip() # Push to dictionary

        # Find Sex field and extract user answer
        sex: str = re.findall("Sex:\s*[a-zA-Z]*\s*\n*", application)[0]
        sex = sex.replace("Sex: ", "")

        data["sex"] = sex.strip() # Push to dictionary

    def __separate_joint_question(answer: str) -> list:
        """Separates joint questions like question 2 which includes answer to 3 datafields 

        Args:
            answer (str): user answer to be separated into multiple answers

        Returns:
            list: of n separate answers
        """

        try:
            separated_answers = answer.split(",")
        except:
            return []

        return separated_answers

        

    def __push_answers(self, data: dict, answers: list) -> None:
        """Go over all answers extracted from user application to push them to corresponding keys in dictionary

        Args:
            data (dict): data strucutre to which user answers will be pushed
            answers (list): user answers extracted from application pdf

        Raises:
            ValueError: If user answers a joint question incorrectly and it is impossible to separate it
        """

        # Iterate though dictionary to add user answers to application questions

        index = 0   # Index of the current question to be pushed into dictionary
        try:
            for key in data:

                # Flag for joint questions where user answered N/A
                is_joint: bool = key in ["workclass","occupation","hours_per_week"]

                if key not in ["race", "sex"]:     # To skip race and sex key/value pairs
                    if is_joint and answers[1] == "N/A":  # If this is a joint question and user answered N/A
                        data[key] = "N/A" # Populate all questions with N/A
                        index = 2
                    elif not is_joint and answers[1] != "N/A": # if joint question but user didn't answer N/A
                        data[key] = self.__separate_joint_question(answers[1])[index - 1]  # Separate each question from a single string
                        index += 1
                    else:
                        data[key] = answers[index]
                        index += 1
        except Exception:
            raise ValueError() # If answer 1 formated incorrectly
                


    def __get_answers(self, data: dict, application: str) -> None:
        """Extract answers to question in loan application pdf

        Args:
            data (dict): data structure to which answers will be pushed
            application (str): string equivalent of user application. See .get_text()
        """

        # Match all fields with "Asnwer: " in it
        answers: list = re.findall("^Answer:\s*[a-zA-Z/\s]+\s*\n*$", application, flags = re.M|re.I)
        
        # Extract user answer from matched lines
        for i in range(0, len(answers)):
            answers[i] = answers[i].replace("Answer: ", "")

        self.__push_answers(data, answers)


    def parse(self) -> dict:
        """Parse loan application pdf. Extracts all relevant data from the pdf file

        Returns:
            dict: dictionary containing answers to question in loan application or an empty dictionary of could't parse file
        """

        usr_data: dict = dict.fromkeys(self.keys) # Create an empty dictionary

        if (application := self.get_text()) != "":

            self.__get_race_and_sex(usr_data, application)
            self.__get_answers(usr_data, application)
            
            return usr_data
                    
        
        return {}


    




       







