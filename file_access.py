from file import File
from user_access import UserAccess

class FileAccess:
    def __init__(self, file: File, user_accesses: list[UserAccess]):
        """
        Represents access permissions to a specific file for multiple users.

        :param file: The File object
        :param user_accesses: List of UserAccess objects
        """
        self.file = file
        self.user_accesses = user_accesses

    def __repr__(self):
        users_info = ", ".join(
            f"{ua.user.username} (ID: {getattr(ua.user, 'id', 'N/A')}, "
            f"read={ua.can_read}, write={ua.can_write})"
            for ua in self.user_accesses
        )
        return f"<FileAccess file={self.file.filename} users=[{users_info}]>"
