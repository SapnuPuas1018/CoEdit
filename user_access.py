from user import User

class UserAccess:
    def __init__(self, user: User, can_read=False, can_write=False):
        """
        Represents access permissions of a user to a specific file.

        :param user: The User object
        :param can_read: Boolean indicating if the user has read access
        :param can_write: Boolean indicating if the user has write access
        """
        self.user = user
        self.can_read = can_read
        self.can_write = can_write

    def __repr__(self):
        user_id = getattr(self.user, 'id', 'N/A')
        return (f"<FileAccess user={self.user.username} (ID: {user_id}) "
                f"read={self.can_read} write={self.can_write}>")
