

class User:
    """
    Represents a user with basic information and file management capabilities.
    """
    def __init__(self, user_id: int, first_name: str, last_name: str,username: str, password):
        """
        Initializes a User object with identification and credentials

        :param user_id: Unique identifier for the user
        :type user_id: int

        :param first_name: First name of the user
        :type first_name: str

        :param last_name: Last name of the user
        :type last_name: str

        :param username: The user's username
        :type username: str

        :param password: The user's password (Note: should be hashed in production)
        :type password:

        :return: None
        """
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password

    def __repr__(self):
        """
        Returns a string representation of the user including their details and file names.

        :return: A string describing the user
        :rtype: str
        """
        return f'user_id: {self.user_id}, first name : {self.first_name}, last name : {self.last_name}, username : {self.username}, password : {self.password}'

if __name__ == '__main__':
    pass