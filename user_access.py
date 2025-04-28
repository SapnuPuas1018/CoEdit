from file import File
from user import User

class UserAccess:
    def __init__(self, file:File, user: User, can_read=False, can_write=False):
        self.file = file
        self.user = user
        self.can_read = can_read
        self.can_write = can_write

    def __repr__(self):
        user_id = getattr(self.user, 'id', 'N/A')
        return (f"<FileAccess user={self.user.username} (ID: {user_id}) "
                f"read={self.can_read} write={self.can_write}>")