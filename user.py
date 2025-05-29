

class User:
    """
    Represents a user with basic information and file management capabilities.
    """
    def __init__(self, user_id, first_name, last_name,username: str, password):
        """
        Initializes a User object with identification, credentials, and an empty file dictionary.

        :param user_id: Unique identifier for the user
        :type user_id: Any

        :param first_name: First name of the user
        :type first_name: Any

        :param last_name: Last name of the user
        :type last_name: Any

        :param username: The user's username
        :type username: str

        :param password: The user's password (Note: should be hashed in production)
        :type password: str

        :return: None
        :rtype: None
        """
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password  # In a real application, store a hashed password!
        self.files = {}  # Dictionary to store files (key: filename, value: content)

    def add_file(self, filename: str, content: str):
        """
        Adds a new file to the user's file list.

        :param filename: Name of the file to add
        :type filename: str

        :param content: Content of the file
        :type content: str

        :return: A message indicating success or if the file already exists
        :rtype: str
        """
        if filename in self.files:
            return f"File '{filename}' already exists."
        self.files[filename] = content
        return f"File '{filename}' added successfully."

    def remove_file(self, filename: str):
        """
        Removes a file from the user's file list if it exists.

        :param filename: Name of the file to remove
        :type filename: str

        :return: A message indicating success or that the file was not found
        :rtype: str
        """
        if filename in self.files:
            del self.files[filename]
            return f"File '{filename}' removed successfully."
        return f"File '{filename}' not found."

    def get_file(self, filename: str):
        """
        Retrieves the content of a file by filename.

        :param filename: Name of the file to retrieve
        :type filename: str

        :return: The content of the file or an error message if not found
        :rtype: str
        """
        return self.files.get(filename, "File not found.")

    def list_files(self):
        """
        Lists all filenames stored by the user.

        :return: A list of filenames
        :rtype: list[str]
        """
        return list(self.files.keys())


    def __repr__(self):
        """
        Returns a string representation of the user including their details and file names.

        :return: A string describing the user
        :rtype: str
        """
        return f'user_id: {self.user_id}, first name : {self.first_name}, last name : {self.last_name}, username : {self.username}, password : {self.password}, files names : {self.list_files()}'

if __name__ == '__main__':
    pass