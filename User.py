
class Person(object):
    """
    Parent class for the 'User' class. 
    
    """

    person_number = 0 # How many unique users are instantiated


    def __init__(self, name: str, age: int) -> None:
        """Instantiate User Object with basic demographic data

        Args:
            name (str): name of the user
            age (int): age of the user
            gender (str): biological gender of the user. M/F
            race (str): race of the user
        """
        self.name = name
        self.age = age
        
        Person.person_number += 1


class User(Person):
    """
    This class holds key user data. It genarates unique user ID and stores a connection of user to the relevant entry in database.

    Extends:
        Person (class)
    """

    def _get_id(self) -> None:
        """Generate a unique ID for the user. Note that this ID is not 'universaly' unique, meaning that uniqueness of this value is true only for local dataset
        """
        try:
            self.user_id = self.name[:4] + str(Person.person_number) + str(self.age)
        except:
            self.user_id = self.name[: len(self.name)] + str(Person.person_number) + str(self.age)

