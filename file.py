from datetime import datetime

class File:
    def __init__(self, filename, content, file_type, owner, creation_date=None):
        self.filename = filename
        self.content = content
        self.file_type = file_type
        self.owner = owner
        self.creation_date = creation_date if creation_date else datetime.now()

    def __repr__(self):
        return f"<File {self.filename}.{self.file_type} by {self.owner} created on {self.creation_date}>"

    def to_tuple(self):
        return (self.filename, self.content, self.file_type, self.owner, self.creation_date.strftime("%Y-%m-%d %H:%M:%S"))