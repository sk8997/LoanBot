import pdfplumber
import re

class LoanApplicationParser(object):

    def __init__(self, file_name: str) -> None:
        
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

    def parse(self) -> dict:

        usr_data: dict = dict.fromkeys(self.keys) # Create an empty dictionary

        if (application := self.get_text()) != "":

            # Find Race field and extract user answer
            race: str = re.findall("Race:\s*[a-zA-Z]*\s*\n*", application)[0]
            race = race.replace("Race: ", "")

            usr_data["race"] = race.strip() # Push to dictionary

            # Find Sex field and extract user answer
            sex: str = re.findall("Sex:\s*[a-zA-Z]*\s*\n*", application)[0]
            sex = sex.replace("Sex: ", "")

            usr_data["sex"] = sex.strip() # Push to dictionary

            # Match all fields with "Asnwer: " in it
            answers: list = re.findall("^Answer:\s*[a-zA-Z/\s]+\s*\n*$", application, flags = re.M|re.I)
            
            # Extract user answer from matched lines
            for i in range(0, len(answers)):
                answers[i] = answers[i].replace("Answer: ", "")

            # Iterate though dictionary to add user answers to application questions

            index = 0   # Index of the current question to be pushed into dictionary
            for key in usr_data:
                if key not in ["race", "sex"]:     # To skip race and sex key/value pairs
                    if key in ["workclass","occupation","hours_per_week"] and answers[1] == "N/A":
                        usr_data[key] = "N/A"
                        index = 2
                    else:
                        usr_data[key] = answers[index]
                        index += 1
            
            return usr_data
                    
        
        return {}

       







