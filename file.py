from datetime import datetime
from uuid import uuid4
from user import User


class File:
    """
    Represents a file object with metadata including filename, owner, path, and creation date.
    """
    def __init__(self, filename, owner: User, path, creation_date=None, file_id=None):
        """
        Initializes a File object with metadata and optional custom creation date and file ID.

        :param filename: The name of the file
        :type filename: str

        :param owner: The user who owns the file
        :type owner: User

        :param path: The path where the file is stored
        :type path: str

        :param creation_date: The date and time the file was created (optional)
        :type creation_date: datetime.datetime or None

        :param file_id: The unique identifier for the file (optional)
        :type file_id: str or None

        :return: None
        :rtype: None
        """
        self.file_id = str(file_id) if file_id else str(uuid4())
        self.filename = filename
        self.owner = owner
        self.path = path
        self.creation_date = creation_date if creation_date else datetime.now()

    def __repr__(self):
        """
        Returns a string representation of the File object, including filename, owner, and creation date.

        :return: A string representation of the File object
        :rtype: str
        """
        return f"<File {self.filename} by {self.owner} created on {self.creation_date}>"

    def to_tuple(self):
        """
        Converts the file attributes to a tuple format suitable for database insertion or transport.

        :return: A tuple containing file_id, owner, filename, path, and formatted creation date
        :rtype: tuple
        """
        return (
            self.file_id,
            self.owner,
            self.filename,
            self.path,
            self.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        )
