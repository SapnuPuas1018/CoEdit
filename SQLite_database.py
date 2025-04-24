import sqlite3
import threading

from file import File
from user import User

class UserDatabase:
    def __init__(self, db_name="users.db"):
        """Initialize SQLite database connection with multi-threading support."""
        self.conn = sqlite3.connect(db_name, check_same_thread=False)  # Allows access across threads
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()  # Thread-safe database access
        self.create_tables()

    def create_tables(self):
        """Create tables for users, files, and access rights."""
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
                    id TEXT PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    creation_date TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_id TEXT,
                    can_read BOOLEAN NOT NULL DEFAULT 0,
                    can_write BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE,
                    UNIQUE(user_id, file_id)
                )
            """)
            self.conn.commit()

    def add_user(self, user):
        """Add a new user to the database."""
        with self.lock:
            try:
                self.cursor.execute(
                    "INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (user.first_name, user.last_name, user.username, user.password),
                )
                self.conn.commit()
                return True, "User added successfully."
            except sqlite3.IntegrityError:
                return False, "Username already exists."

    def verify_user(self, user):
        """Verify user login credentials."""
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (user.username, user.password))
            return self.cursor.fetchone() is not None

    # def user_exists(self, username):
    #     """Check if a user exists in the database."""
    #     with self.lock:
    #         self.cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    #         return self.cursor.fetchone() is not None

    def add_file(self, user, file: File, content):
        """Add a file for a user."""
        owner_id = self.get_user_id(user.username)
        if owner_id:
            with self.lock:
                self.cursor.execute(
                    "INSERT INTO files (id, owner_id, filename, content) VALUES (?, ?, ?, ?)",
                    (file.file_id, owner_id, file.filename, content),
                )
                self.conn.commit()
                return True, f"File '{file.filename}' added successfully."
        return False, "User not found."

    def get_file_content(self, user, filename):
        """Retrieve the content of a specific file."""
        owner_id = self.get_user_id(user.username)
        if owner_id:
            with self.lock:
                self.cursor.execute(
                    "SELECT content FROM files WHERE owner_id=? AND filename=?", (owner_id, filename)
                )
                result = self.cursor.fetchone()
                return result[0] if result else None
        return None

    def remove_file(self, username, filename):
        """Delete a file from the database."""
        owner_id = self.get_user_id(username)
        if owner_id:
            with self.lock:
                self.cursor.execute("DELETE FROM files WHERE owner_id=? AND filename=?", (owner_id, filename))
                self.conn.commit()
                return True, f"File '{filename}' removed successfully."
        return False, "User not found."

    def get_user_id(self, username):
        """Retrieve user ID from username."""
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    def can_user_read_file(self, user: User, file: File) -> bool:
        user_id = self.get_user_id(user.username)
        file_id = file.file_id
        with self.lock:
            self.cursor.execute(
                "SELECT can_read FROM file_access WHERE user_id=? AND file_id=?", (user_id, file_id)
            )
            result = self.cursor.fetchone()
            return result[0] if result else False


    def can_user_write_file(self, user: User, file: File) -> bool:
        user_id = self.get_user_id(user.username)
        file_id = file.file_id
        with self.lock:
            self.cursor.execute(
                "SELECT can_write FROM file_access WHERE user_id=? AND file_id=?", (user_id, file_id)
            )
            result = self.cursor.fetchone()
            return result[0] if result else False

    def get_readable_files_per_user(self, user):
        """Retrieve all files the user has read access to as File objects."""
        user_id = self.get_user_id(user.username)
        with self.lock:
            self.cursor.execute("""
                SELECT f.id, f.filename, f.content, f.owner_id, f.creation_date
                FROM files f
                JOIN file_access fa ON f.id = fa.file_id
                WHERE fa.user_id = ? AND fa.can_read = 1
            """, (user_id,))

            rows = self.cursor.fetchall()
            readable_files = []
            for row in rows:
                file = File(
                    file_id=row[0],
                    filename=row[1],
                    content=row[2],
                    owner=row[3],
                    creation_date=row[4]
                )
                readable_files.append(file)
            return readable_files

    def add_file_access(self, user: User, file: File, can_read=False, can_write=False):
        """Grant or update read/write access to a file for a specific user."""
        file_id = file.file_id
        user_id = self.get_user_id(user.username)
        if user_id is None:
            return False

        with self.lock:
            # Insert new access rights
            self.cursor.execute("""
                INSERT INTO file_access (user_id, file_id, can_read, can_write)
                VALUES (?, ?, ?, ?)
            """, (user_id, file_id, int(can_read), int(can_write)))

            self.conn.commit()
            return True

    def change_file_access(self, user: User, file: File, can_read: bool, can_write: bool):
        file_id = file.file_id
        user_id = self.get_user_id(user.username)
        if user_id is None:
            return False
        with self.lock:
            # Update existing access rights
            self.cursor.execute("""
                UPDATE file_access
                SET can_read = ?, can_write = ?
                WHERE user_id = ? AND file_id = ?
            """, (int(can_read), int(can_write), user_id, file_id))
            self.conn.commit()
            return True


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

    user = User("John", "Doe", "jd123", "securepassword123")
    print(db.add_user(user))
    print(db.get_user_full_name("jd123"))
    print(db.add_file(user, "notes.txt", 'context in file'))
    print(db.get_files(user))
    print(db.get_file_content(user, "notes.txt"))
    print(db.remove_file("jd123", "notes.txt"))
    print(db.get_files(user))
    db.close()
