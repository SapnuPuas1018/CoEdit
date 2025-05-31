import os
import sqlite3
import threading

import bcrypt

from file import File
from user import User
from user_access import UserAccess


class Database:
    def __init__(self, db_name="users.db"):
        """
        Initialize the UserDatabase with a SQLite connection and create tables if they do not exist.

        :param db_name: Name of the SQLite database file
        :type db_name: str
        """
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self.create_tables()

    def create_tables(self):
        """
        Create the required database tables for users, files, and file access permissions.
        """
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL
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
        """
        Add a new user to the database.

        :param user: The User object containing user information
        :type user: User

        :return: True if the user was added successfully, False otherwise
        :rtype: bool
        """
        with self.lock:
            try:
                self.cursor.execute(
                    "INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (user.first_name, user.last_name, user.username, user.password),
                )
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, user: User):
        """
        Verify user credentials during login.

        :param user: The User object containing username and password
        :type user: User

        :return: Tuple of (login_successful, user_id)
        :rtype: tuple[bool, int or None]
        """
        user_id = self.get_user_id(user.username)
        with self.lock:
            self.cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
            row = self.cursor.fetchone()

            if row is None:
                return False, None

            stored_hashed_password = row[0]

            password_matches = bcrypt.checkpw(user.password.encode('utf-8'), stored_hashed_password)

            return password_matches, user_id if password_matches else None

    def add_file(self, user: User, file: File, content: str):
        """
        Add a file to the database and save its content to disk.

        :param user: The owner User object
        :type user: User
        :param file: The File object to be saved
        :type file: File
        :param content: Content to write to the file
        :type content: str

        :return: Tuple indicating success and a message
        :rtype: tuple[bool, str]
        """
        if not user.user_id:
            return False

        base_dir = os.path.join("CoEdit_users", user.username)
        os.makedirs(base_dir, exist_ok=True)  # create a directory if doesnt exist

        full_path = os.path.join(base_dir, file.filename)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            with self.lock:
                self.cursor.execute(
                    "INSERT INTO files (id, owner_id, filename, path) VALUES (?, ?, ?, ?)",
                    (file.file_id, user.user_id, file.filename, full_path),
                )
                self.conn.commit()

            return True

        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def get_file_content(self, user: User, file: File):
        """
        Retrieve file content from disk if the user has read access.

        :param user: The User object
        :type user: User
        :param file: The File object
        :type file: File

        :return: The content of the file or None if inaccessible
        :rtype: str or None
        """
        if not self.can_user_read(user, file):
            print("User does not have read access")
            return None

        with self.lock:
            self.cursor.execute("SELECT path FROM files WHERE id = ?", (file.file_id,))
            result = self.cursor.fetchone()

        if result:
            path = result[0]
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    print(f'get_file_content, path: {path}, file_content: {file_content}')
                    return file_content or ''
            except FileNotFoundError:
                return None
        return ''

    def update_file_content(self, user: User, file: File, content: str) -> bool:
        """
        Retrieve file content from disk if the user has read access.

        :param user: The User object
        :type user: User
        :param file: The File object
        :type file: File
        :param content: The new content to be saved
        :type content: str

        :return: The content of the file or None if inaccessible
        :rtype: str or None
        """
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
                        print(f'updated to file, path: {path}, content: {content}')
                        f.write(content)
                    return True
                except Exception as e:
                    print("Error writing file:", e)
                    return False
        return False

    def delete_file(self, user_id, file_id):
        """
        Deletes a file from both the database and disk.

        :param user_id: ID of the file owner
        :type user_id: int
        :param file_id: ID of the file to be removed
        :type file_id: str

        :return: Tuple of success status and a message
        :rtype: tuple[bool, str]
        """
        with self.lock:
            self.cursor.execute("SELECT path FROM files WHERE id=? AND owner_id=?", (file_id, user_id))
            result = self.cursor.fetchone()

            if result:
                path = result[0]
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"Warning: Failed to delete file from disk: {e}")

                self.cursor.execute("DELETE FROM files WHERE id=? AND owner_id=?", (file_id, user_id))
                self.conn.commit()
                return True
        return False

    def get_user_id(self, username):
        """
        Retrieve the user ID from a username.

        :param username: The username to search for
        :type username: str

        :return: User ID or None if not found
        :rtype: int or None
        """
        with self.lock:
            self.cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None

    def check_if_user_exists_by_username(self, username: str):
        """
        Check if a user exists by username and return the User object if found.

        :param username: Username to check
        :type username: str

        :return: User object if found, else None
        :rtype: User or None
        """
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

    def can_user_read(self, user: User, file: File) -> bool:
        """
        Check if the user has read access to a specific file.

        :param user: The User object
        :type user: User
        :param file: The File object
        :type file: File

        :return: True if user can read the file, False otherwise
        :rtype: bool
        """
        with self.lock:
            self.cursor.execute(
                "SELECT can_read FROM file_access WHERE user_id=? AND file_id=?", (user.user_id, file.file_id)
            )
            result = self.cursor.fetchone()
            return result[0] if result else False

    def can_user_write(self, user: User, file: File) -> bool:
        """
        Check if a user can write to a file (as owner or shared write access).

        :param user: The User object
        :type user: User
        :param file: The File object
        :type file: File

        :return: True if the user can write to the file, False otherwise
        :rtype: bool
        """
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
        """
        Get all files the user has read access to.

        :param user: The User object
        :type user: User

        :return: List of File objects the user can read
        :rtype: list[File]
        """
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

    def add_file_access(self, user: User, file: File, can_read=False, can_write=False):
        """
        Grant file access rights to a user.

        :param user: The User object receiving access
        :type user: User
        :param file: The File object to share
        :type file: File
        :param can_read: Permission to read the file
        :type can_read: bool
        :param can_write: Permission to write to the file
        :type can_write: bool

        :return: True if access was granted successfully
        :rtype: bool
        """
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
        """
        Change access rights to a file for a user.

        :param user: The User object
        :type user: User
        :param file: The File object
        :type file: File
        :param can_read: Updated read access
        :type can_read: bool
        :param can_write: Updated write access
        :type can_write: bool

        :return: True if access rights were updated or inserted successfully
        :rtype: bool
        """
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
                self.cursor.execute("""
                    INSERT INTO file_access (user_id, file_id, can_read, can_write)
                    VALUES (?, ?, ?, ?)
                """, (user_id, file_id, int(can_read), int(can_write)))

            self.conn.commit()
            return True

    def get_users_with_access_to_file(self, file: File) -> list[UserAccess]:
        """
        Retrieve a list of all users who have access to a file, including read and write permissions.

        :param file: The File object
        :type file: File

        :return: List of UserAccess objects
        :rtype: list[UserAccess]
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
        """
        Rename a file both on disk and in the database.

        :param file: The File object to rename
        :type file: File
        :param new_filename: New filename to assign
        :type new_filename: str

        :return: True if renamed successfully, False otherwise
        :rtype: bool
        """
        with self.lock:
            self.cursor.execute("SELECT path FROM files WHERE id = ?", (file.file_id,))
            result = self.cursor.fetchone()
            if not result:
                return False  # file not found

            old_path = result[0]
            new_path = os.path.join(os.path.dirname(old_path), new_filename)

            try:
                os.rename(old_path, new_path)
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
        """
        Retrieve the full name of a user based on the given username.

        :param username: The username of the user whose full name is to be retrieved
        :type username: str

        :return: A tuple containing (first_name, last_name) if the user exists, otherwise None
        :rtype: tuple or None
        """
        with self.lock:
            self.cursor.execute("SELECT first_name, last_name FROM users WHERE username=?", (username,))
            result = self.cursor.fetchone()
            return result[0],result[1] if result else None

    def close_connection(self):
        """
        Close the database connection.

        :return: None
        """
        with self.lock:
            self.conn.close()
