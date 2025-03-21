import sqlite3
import threading


class UserDatabase:
    def __init__(self, db_name="users.db"):
        """Initialize SQLite database connection with multi-threading support."""
        self.conn = sqlite3.connect(db_name, check_same_thread=False)  # Allows access across threads
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()  # Thread-safe database access
        self.create_tables()

    def create_tables(self):
        """Create tables for users and their files."""
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()

    def add_user(self, first_name, last_name, username, password):
        """Add a new user to the database."""
        with self.lock:
            try:
                self.cursor.execute(
                    "INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (first_name, last_name, username, password),
                )
                self.conn.commit()
                return True, "User added successfully."
            except sqlite3.IntegrityError:
                return False, "Username already exists."

    def verify_user(self, username, password):
        """Verify user login credentials."""
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
            return self.cursor.fetchone() is not None

    def user_exists(self, username):
        """Check if a user exists in the database."""
        with self.lock:
            self.cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
            return self.cursor.fetchone() is not None

    def add_file(self, username, filename, content):
        """Add a file for a user."""
        user_id = self.get_user_id(username)
        if user_id:
            with self.lock:
                self.cursor.execute(
                    "INSERT INTO files (user_id, filename, content) VALUES (?, ?, ?)",
                    (user_id, filename, content),
                )
                self.conn.commit()
                return True, f"File '{filename}' added successfully."
        return False, "User not found."

    def get_files(self, username):
        """Retrieve all files of a user."""
        user_id = self.get_user_id(username)
        if user_id:
            with self.lock:
                self.cursor.execute("SELECT filename FROM files WHERE user_id=?", (user_id,))
                return [row[0] for row in self.cursor.fetchall()]
        return []

    def get_file_content(self, username, filename):
        """Retrieve the content of a specific file."""
        user_id = self.get_user_id(username)
        if user_id:
            with self.lock:
                self.cursor.execute(
                    "SELECT content FROM files WHERE user_id=? AND filename=?", (user_id, filename)
                )
                result = self.cursor.fetchone()
                return result[0] if result else None
        return None

    def remove_file(self, username, filename):
        """Delete a file from the database."""
        user_id = self.get_user_id(username)
        if user_id:
            with self.lock:
                self.cursor.execute("DELETE FROM files WHERE user_id=? AND filename=?", (user_id, filename))
                self.conn.commit()
                return True, f"File '{filename}' removed successfully."
        return False, "User not found."

    def get_user_id(self, username):
        """Retrieve user ID from username."""
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    def get_user_full_name(self, username):
        """Retrieve the full name of a user."""
        with self.lock:
            self.cursor.execute("SELECT first_name, last_name FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return f"{result[0]} {result[1]}" if result else None

    def close(self):
        """Close the database connection."""
        with self.lock:
            self.conn.close()


# Example Usage
if __name__ == "__main__":
    db = UserDatabase()


    print(db.add_user("John", "Doe", "jd123", "securepassword123"))
    print(db.get_user_full_name("jd123"))


    print(db.add_file("jd123", "notes.txt", "This is a sample note."))
    print(db.get_files("jd123"))


    print(db.get_file_content("jd123", "notes.txt"))
    print(db.remove_file("jd123", "notes.txt"))


    print(db.get_files("jd123"))
    print(db.user_exists("jd123"))
    print(db.user_exists("unknown_user"))

    db.close()
