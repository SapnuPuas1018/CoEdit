# import sqlite3
# from user import User
# conn = sqlite3.connect('users.db')
# c = conn.cursor()
#
#
# user1 = User('Messi', '123', '')
#
#
#
# def add_user(user):
#     c.execute(f'INSERT INTO users VALUES ({user.name}, {user.password})')
#     conn.commit()
#
# c.execute("""CREATE TABLE users (
#             name text
#             password text
#     )""")
#
# conn.commit()
# conn.close()
import sqlite3

class UserDatabase:
    def __init__(self, db_name="users.db"):
        """Initialize SQLite database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create tables for users and their files."""
        # create user table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # create file table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT,
                content TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def add_user(self, name, password):
        """Add a new user to the database."""
        try:
            self.cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
            self.conn.commit()
            return "User added successfully."
        except sqlite3.IntegrityError:
            return "Username already exists."

    def verify_user(self, name, password):
        """Verify user login credentials."""
        self.cursor.execute("SELECT id FROM users WHERE name=? AND password=?", (name, password))
        return self.cursor.fetchone()

    def add_file(self, user_name, filename, content):
        """Add a text file for a user."""
        user_id = self.get_user_id(user_name)
        if user_id:
            self.cursor.execute("INSERT INTO files (user_id, filename, content) VALUES (?, ?, ?)",
                                (user_id, filename, content))
            self.conn.commit()
            return f"File '{filename}' added."
        return "User not found."

    def get_files(self, user_name):
        """Retrieve all files of a user."""
        user_id = self.get_user_id(user_name)
        if user_id:
            self.cursor.execute("SELECT filename FROM files WHERE user_id=?", (user_id,))
            return [row[0] for row in self.cursor.fetchall()]
        return "User not found."

    def get_file_content(self, user_name, filename):
        """Retrieve a specific file's content."""
        user_id = self.get_user_id(user_name)
        if user_id:
            self.cursor.execute("SELECT content FROM files WHERE user_id=? AND filename=?",
                                (user_id, filename))
            result = self.cursor.fetchone()
            return result[0] if result else "File not found."
        return "User not found."

    def remove_file(self, user_name, filename):
        """Delete a file from the database."""
        user_id = self.get_user_id(user_name)
        if user_id:
            self.cursor.execute("DELETE FROM files WHERE user_id=? AND filename=?", (user_id, filename))
            self.conn.commit()
            return f"File '{filename}' removed."
        return "User not found."

    def get_user_id(self, name):
        """Retrieve user ID from username."""
        self.cursor.execute("SELECT id FROM users WHERE name=?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Example usage:
db = UserDatabase()
print(db.add_user("JohnDoe", "securepassword123"))
print(db.add_file("JohnDoe", "notes.txt", "This is a sample note."))
print(db.get_files("JohnDoe"))
print(db.get_file_content("JohnDoe", "notes.txt"))
print(db.remove_file("JohnDoe", "notes.txt"))
print(db.get_files("JohnDoe"))
db.close()
