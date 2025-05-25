from file import File
from user_access import UserAccess
from typing import List

class FileAccess:
    """
    Represents access control information for a specific file,
    including which users have read and/or write permissions.

    Attributes:
        file (File): The file to which access is managed.
        user_accesses (List[UserAccess]): A list of UserAccess entries detailing each user's permissions.
    """

    def __init__(self, file: File, user_accesses: List[UserAccess]):
        """
        Initializes a FileAccess instance.

        :param file: The File object for which access is defined.
        :param user_accesses: List of UserAccess objects representing user permissions.
        """
        self.file = file
        self.user_accesses = user_accesses

    def __repr__(self) -> str:
        """
        Returns a human-readable string representation of the file and its user access permissions.

        :return: A string describing the file and each user's read/write access.
        """
        users_info = ", ".join(
            f"{ua.user.username} (ID: {getattr(ua.user, 'id', 'N/A')}, "
            f"read={ua.can_read}, write={ua.can_write})"
            for ua in self.user_accesses
        )
        return f"<FileAccess file={self.file.filename} users=[{users_info}]>"
