from datetime import datetime
from uuid import uuid4

from user import User


class File:
    def __init__(self, filename, owner: User, path, creation_date=None, file_id=None):
        self.file_id = str(file_id) if file_id else str(uuid4())
        self.filename = filename
        self.owner = owner
        self.path = path
        self.creation_date = creation_date if creation_date else datetime.now()

    def __repr__(self):
        return f"<File {self.filename} by {self.owner} created on {self.creation_date}>"

    def to_tuple(self):
        return (
            self.file_id,
            self.owner,
            self.filename,
            self.path,
            self.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        )
