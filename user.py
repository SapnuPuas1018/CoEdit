
class User:
    def __init__(self, name: str, password: str):
        """Initialize a user with a name, password, and an empty list of files."""
        self.name = name
        self.password = password  # In a real application, store a hashed password!
        self.files = {}  # Dictionary to store files (key: filename, value: content)

    def add_file(self, filename: str, content: str):
        """Add a new text file to the user's file collection."""
        if filename in self.files:
            return f"File '{filename}' already exists."
        self.files[filename] = content
        return f"File '{filename}' added successfully."

    def remove_file(self, filename: str):
        """Remove a file from the user's collection."""
        if filename in self.files:
            del self.files[filename]
            return f"File '{filename}' removed successfully."
        return f"File '{filename}' not found."

    def get_file(self, filename: str):
        """Retrieve the content of a specific file."""
        return self.files.get(filename, "File not found.")

    def list_files(self):
        """Return a list of all file names."""
        return list(self.files.keys())

    def verify_password(self, password: str):
        """Verify if the given password matches the user's password (insecure method, just for demo)."""
        return self.password == password  # In real cases, use hashing!

# Example usage:
user1 = User("JohnDoe", "securepassword123")
print(user1.add_file("notes.txt", "This is a sample text file."))
print(user1.add_file("todo.txt", "Buy milk\nComplete project."))
print(user1.list_files())
print(user1.get_file("notes.txt"))
print(user1.remove_file("todo.txt"))
print(user1.list_files())
