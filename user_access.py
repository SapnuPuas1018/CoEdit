from file import File
from user import User

class UserAccess:
    """
    Manages a user's access permissions (read/write) to a specific file.
    """
    def __init__(self, file:File, user: User, can_read=False, can_write=False):
        """
        Initializes a UserAccess object with file, user, and access permissions.

        :param file: The file to which access is being granted
        :type file: File

        :param user: The user who is being granted access
        :type user: User

        :param can_read: Specifies if the user has read access to the file
        :type can_read: bool

        :param can_write: Specifies if the user has write access to the file
        :type can_write: bool

        :return: None
        :rtype: None
        """
        self.file = file
        self.user = user
        self.can_read = can_read
        self.can_write = can_write

    def __repr__(self):
        """
        Returns a string representation of the UserAccess object, showing user info and access rights.

        :return: A string representation of the access permissions for the user
        :rtype: str
        """
        user_id = getattr(self.user, 'id', 'N/A')
        return (f"<FileAccess user={self.user.username} (ID: {user_id}) "
                f"read={self.can_read} write={self.can_write}>")