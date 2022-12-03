import pdfplumber

class LoanApplicationParser(object):

    def __init__(self, file_name: str) -> None:
        
        self.file_name = file_name

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

