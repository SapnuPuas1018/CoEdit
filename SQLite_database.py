import os
import sqlite3
import threading

from file import File
from user import User
from user_access import UserAccess


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
                    path TEXT NOT NULL,
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

    def add_user(self, user: User):
        """Add a new user to the database."""
        with self.lock:
            try:
                self.cursor.execute(
                    "INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (user.first_name, user.last_name, user.username, user.password),
                )
                self.conn.commit()
                # user_id = self.cursor.lastrowid
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, user: User):
        """Verify user login credentials."""
        user_id = self.get_user_id(user.username)
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE id=? AND password=?", (user_id, user.password))
            return self.cursor.fetchone() is not None, user_id

    def add_file(self, user: User, file: File, content: str):
        """Save file content to disk and record its path in the database."""

        if not user.user_id:
            return False, "User not found."

        # Build directory path
        base_dir = os.path.join("CoEdit_users", user.username)
        os.makedirs(base_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Build full file path
        full_path = os.path.join(base_dir, file.filename)

        try:
            # Save file content to disk
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Save file metadata and path in DB
            with self.lock:
                self.cursor.execute(
                    "INSERT INTO files (id, owner_id, filename, path) VALUES (?, ?, ?, ?)",
                    (file.file_id, user.user_id, file.filename, full_path),
                )
                self.conn.commit()

            return True, f"File '{file.filename}' saved to disk and registered in database."

        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def get_file_content(self, user: User, file: File):
        """Retrieve the content of a file from disk if the user has read access."""
        print('hi')
        with self.lock:
            # Check if the user has read access
            self.cursor.execute("""
                SELECT can_read FROM file_access 
                JOIN users ON file_access.user_id = users.id 
                WHERE users.username = ? AND file_access.file_id = ?
            """, (user.username, file.file_id))
            access_result = self.cursor.fetchone()

            if not access_result or not access_result[0]:
                return None  # User has no read access

            # Retrieve file path
            self.cursor.execute("SELECT path FROM files WHERE id = ?", (file.file_id,))
            result = self.cursor.fetchone()

        if result:
            path = result[0]
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return None
        return None

    def save_file_content(self, user: User, file: File, content: str) -> bool:
        if not self.can_user_write(user, file):
            print("User does not have write access")
            return False

        with self.lock:
            self.cursor.execute("SELECT path FROM files WHERE id = ?", (file.file_id,))
            result = self.cursor.fetchone()
            print("Stored file path:", result[0])
            if result:
                print(result[0])
                path = result[0]
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        print('i opened the file')
                        f.write(content)
                    return True
                except Exception as e:
                    print("Error writing file:", e)
                    return False
        return False

    def get_file_path(self, user: User, filename):
        """Retrieve the file path instead of content."""
        owner_id = self.get_user_id(user.username)
        if owner_id:
            with self.lock:
                self.cursor.execute(
                    "SELECT path FROM files WHERE owner_id=? AND filename=?", (owner_id, filename)
                )
                result = self.cursor.fetchone()
                return result[0] if result else None
        return None

    def remove_file(self, user_id, file_id):
        """Delete a file from the database and disk using file_id and user_id."""
        with self.lock:
            # Confirm the file belongs to the user
            self.cursor.execute("SELECT path FROM files WHERE id=? AND owner_id=?", (file_id, user_id))
            result = self.cursor.fetchone()

            if result:
                path = result[0]
                # Delete from disk
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"Warning: Failed to delete file from disk: {e}")

                # Delete file entry and associated access
                self.cursor.execute("DELETE FROM files WHERE id=? AND owner_id=?", (file_id, user_id))
                self.conn.commit()
                return True, f"File '{file_id}' removed successfully."
        return False, "File not found or access denied."

    def get_user_id(self, username):
        """Retrieve user ID from username."""
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    def check_if_user_exists_by_username(self, username: str):
        self.cursor.execute("""
            SELECT id, first_name, last_name, username, password
            FROM users
            WHERE username = ?
        """, (username,))
        row = self.cursor.fetchone()
        if row:
            user_id, first_name, last_name, username, password = row
            return User(user_id, first_name, last_name, username, password)
        else:
            return None

    def can_user_read_file(self, user: User, file: File) -> bool:
        with self.lock:
            self.cursor.execute(
                "SELECT can_read FROM file_access WHERE user_id=? AND file_id=?", (user.user_id, file.file_id)
            )
            result = self.cursor.fetchone()
            return result[0] if result else False


    # def can_user_write_file(self, user: User, file: File) -> bool:
    #     user_id = self.get_user_id(user.username)
    #     file_id = file.file_id
    #     with self.lock:
    #         self.cursor.execute(
    #             "SELECT can_write FROM file_access WHERE user_id=? AND file_id=?", (user_id, file_id)
    #         )
    #         result = self.cursor.fetchone()
    #         return result[0] if result else False

    def can_user_write(self, user: User, file: File) -> bool:
        with self.lock:
            self.cursor.execute("""
                SELECT 1 FROM files 
                WHERE id = ? AND owner_id = (SELECT id FROM users WHERE username = ?)
            """, (file.file_id, user.username))
            if self.cursor.fetchone():
                return True
            self.cursor.execute("""
                SELECT can_write FROM file_access 
                JOIN users ON file_access.user_id = users.id 
                WHERE users.username = ? AND file_access.file_id = ?
            """, (user.username, file.file_id))
            result = self.cursor.fetchone()
            return bool(result and result[0])

    def get_readable_files_per_user(self, user: User) -> list[File]:
        """Retrieve all files the user has read access to as File objects with owner as a User object."""
        with self.lock:
            self.cursor.execute("""
                SELECT f.id, f.filename, f.path, f.creation_date,
                       u.id, u.first_name, u.last_name, u.username, u.password
                FROM files f
                JOIN file_access fa ON f.id = fa.file_id
                JOIN users u ON f.owner_id = u.id
                WHERE fa.user_id = ? AND fa.can_read = 1
            """, (user.user_id,))

            rows = self.cursor.fetchall()
            readable_files = []
            for row in rows:
                file_id, filename, path, creation_date = row[:4]
                owner = User(
                    user_id=row[4],
                    first_name=row[5],
                    last_name=row[6],
                    username=row[7],
                    password=''
                )
                file = File(
                    file_id=file_id,
                    filename=filename,
                    path=path,
                    owner=owner,
                    creation_date=creation_date
                )
                readable_files.append(file)
            return readable_files

    def get_user_by_id(self, user_id: int):
        """Retrieve a user object from the database using their ID."""
        with self.lock:
            self.cursor.execute("""
                SELECT id, first_name, last_name, username
                FROM users
                WHERE id = ?
            """, (user_id,))
            row = self.cursor.fetchone()
            if row:
                return User(
                    user_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    username=row[3],
                    password=row[4]
                )
            return None

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
            # First, check if an entry already exists
            self.cursor.execute("""
                SELECT id FROM file_access WHERE user_id = ? AND file_id = ?
            """, (user_id, file_id))
            result = self.cursor.fetchone()

            if result:
                # Entry exists -> Update
                self.cursor.execute("""
                    UPDATE file_access
                    SET can_read = ?, can_write = ?
                    WHERE user_id = ? AND file_id = ?
                """, (int(can_read), int(can_write), user_id, file_id))
            else:
                # Entry does not exist -> Insert
                self.cursor.execute("""
                    INSERT INTO file_access (user_id, file_id, can_read, can_write)
                    VALUES (?, ?, ?, ?)
                """, (user_id, file_id, int(can_read), int(can_write)))

            self.conn.commit()
            return True

    def get_users_with_access_to_file(self, file: File) -> list[UserAccess]:
        """
        Retrieve a list of UserAccess objects for a specific file, including all users who have access to it.
        """
        with self.lock:
            self.cursor.execute("""
                SELECT u.id, u.first_name, u.last_name, u.username, fa.can_read, fa.can_write
                FROM file_access fa
                JOIN users u ON fa.user_id = u.id
                WHERE fa.file_id = ?
            """, (file.file_id,))

            rows = self.cursor.fetchall()
            user_accesses = []

            for row in rows:
                user_id = row[0]
                first_name = row[1]
                last_name = row[2]
                username = row[3]
                can_read = row[4]
                can_write = row[5]

                user = User(user_id, first_name=first_name, last_name=last_name, username=username, password='')

                user_access = UserAccess(file= file, user=user, can_read=bool(can_read), can_write=bool(can_write))
                user_accesses.append(user_access)

            return user_accesses

    def rename_file(self, file: File, new_filename: str) -> bool:
        """Rename a file by updating both the filename on disk and in the database."""
        with self.lock:
            # Get current file path
            self.cursor.execute("SELECT path FROM files WHERE id = ?", (file.file_id,))
            result = self.cursor.fetchone()
            if not result:
                return False  # File not found in DB

            old_path = result[0]
            new_path = os.path.join(os.path.dirname(old_path), new_filename)

            try:
                # Rename the file on disk
                os.rename(old_path, new_path)

                # Update database: filename and path
                self.cursor.execute(
                    "UPDATE files SET filename = ?, path = ? WHERE id = ?",
                    (new_filename, new_path, file.file_id)
                )
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error renaming file: {e}")
                return False

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
