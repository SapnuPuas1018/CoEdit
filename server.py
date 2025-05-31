import socket
import ssl
from threading import Thread, Lock, Timer

import protocol
from SQLite_database import UserDatabase
from file import File
from operation import Operation
from request import Request
from user import User

IP_ADDR = '0.0.0.0'
PORT = 8468
QUEUE_LEN = 1
CERT_FILE = 'certificate.crt'
KEY_FILE = 'privateKey.key'
UPDATE_INTERVAL = 0.8  # 800ms


class Server:
    def __init__(self):
        self.open_files = {}
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(CERT_FILE, KEY_FILE)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((IP_ADDR, PORT))
        self.server_socket.listen(QUEUE_LEN)

        self.s_sock = self.context.wrap_socket(self.server_socket, server_side=True)
        self.thread_list = []
        self.database = UserDatabase()

        # Add pending changes queue and lock for thread safety
        self.pending_changes = {}  # {file_id: {conn: [changes]}}
        self.pending_changes_lock = Lock()

        # Start the timer for sending batched updates
        self.update_timer = None
        self.start_update_timer()

    def start_update_timer(self):
        """
        Start a timer that triggers the sending of batched file content updates every UPDATE_INTERVAL seconds.

        :return: None
        """
        self.update_timer = Timer(UPDATE_INTERVAL, self.send_batched_updates)
        self.update_timer.daemon = True
        self.update_timer.start()

    def send_batched_updates(self):
        """
                Send all pending file content changes to appropriate clients with read access, and schedule the next update.

                :return: None
        """
        try:
            with self.pending_changes_lock:
                for file_id, conn_changes in list(self.pending_changes.items()):
                    if file_id not in self.open_files:
                        continue

                    for sender_conn, changes in list(conn_changes.items()):
                        if not changes:
                            continue

                        file = changes[0][0]
                        all_changes = []
                        for _, change_list in changes:
                            all_changes.extend(change_list)

                        print(f"Broadcasting changes for file {file_id} from sender {sender_conn}")

                        for user, conn in self.open_files.get(file_id, []):
                            if conn == sender_conn:
                                continue

                            print(f"Checking read access for {user.username} on file {file_id}")
                            if self.database.can_user_read_file(user, file):
                                print(f"User {user.username} has read access, sending update.")
                                try:
                                    protocol.send(conn, Request('file-content-update', [file, all_changes]))
                                except Exception as e:
                                    print(f"Error sending batched update to {user.username}: {e}")
                            else:
                                print(f"User {user.username} does NOT have read access.")

                self.pending_changes.clear()

        except Exception as e:
            print(f"Error in send_batched_updates: {e}")

        finally:
            self.start_update_timer()

    def start_server(self):
        """
        Start the server to listen for incoming SSL connections and spawn a new thread for each client.

        :return: None
        """
        while True:
            conn, addr = self.s_sock.accept()
            print(f'received a connection from {conn}, {addr}')
            thread = Thread(target=self.listen, args=(conn,))
            thread.start()
            self.thread_list.append(thread)

    def listen(self, conn):
        """
                Continuously listen for requests from a specific client and delegate request handling.

                :param conn: SSL-wrapped socket connection with the client
                :type conn: ssl.SSLSocket

                :return: None
        """
        try:
            while True:
                msg = protocol.recv(conn)
                print(f'received a msg from {conn}, msg {msg}')
                self.handle_request(msg, conn)
        except socket.error as sock_err:
            print(sock_err)
        finally:
            conn.close()
            self.cleanup_connection(conn)

    def cleanup_connection(self, conn):
        """
        Clean up all references to a disconnected client connection from open files and pending changes.

        :param conn: The client connection to clean up
        :type conn: ssl.SSLSocket

        :return: None
        """
        # Remove connection from open_files
        for file_id in list(self.open_files):
            self.open_files[file_id] = [(u, c) for u, c in self.open_files[file_id] if c != conn]
            if not self.open_files[file_id]:
                del self.open_files[file_id]

        # Remove connection from pending_changes
        with self.pending_changes_lock:
            for file_id in list(self.pending_changes):
                if conn in self.pending_changes[file_id]:
                    del self.pending_changes[file_id][conn]
                if not self.pending_changes[file_id]:
                    del self.pending_changes[file_id]

    def handle_request(self, request: Request, conn):
        """
        Route a received request to the appropriate handler function based on its type.

        :param request: The incoming request object
        :type request: Request
        :param conn: The SSL-wrapped socket connection with the client
        :type conn: ssl.SSLSocket

        :return: None
        """
        print(f"received from client : {request}")
        if request.request_type == 'signup':
            self.handle_signup(request, conn)
            return
        elif request.request_type == 'login':
            self.handle_login(request, conn)
            return
        elif request.request_type == 'add-file':
            self.handle_add_file(request, conn)
        elif request.request_type == 'refresh-files':
            user = request.data
            self.get_user_files(user, conn)
        elif request.request_type == 'rename-file':
            self.handle_file_rename(request, conn)
        elif request.request_type == 'delete-file':
            pass
        elif request.request_type == "open-file":
            self.handle_open_file(request.data[0], request.data[1], conn)
        elif request.request_type == 'get-access-list':
            self.handle_get_access_list(request, conn)
        elif request.request_type == 'check-user-exists':
            self.handle_check_user_exists(request, conn)
        elif request.request_type == 'update-access-table':
            self.handle_update_access_table(request, conn)
        elif request.request_type == 'file-content-update':
            self.handle_file_content_update(request, conn)
        elif request.request_type == 'logout':
            self.handle_logout(request.data, conn)

    def handle_logout(self, user: User, conn):
        """
        Handle user logout: clean up all user-related state but keep the connection open.

        :param user: The user who is logging out
        :type user: User
        :param conn: The SSL-wrapped connection still in use
        :type conn: ssl.SSLSocket

        :return: None
        """
        print(f"User {user.username} is logging out...")

        # Clean up open_files
        for file_id in list(self.open_files):
            self.open_files[file_id] = [(u, c) for u, c in self.open_files[file_id] if c != conn]
            if not self.open_files[file_id]:
                del self.open_files[file_id]

        # Clean up pending_changes
        with self.pending_changes_lock:
            for file_id in list(self.pending_changes):
                if conn in self.pending_changes[file_id]:
                    del self.pending_changes[file_id][conn]
                if not self.pending_changes[file_id]:
                    del self.pending_changes[file_id]

        print(f"User {user.username} logged out and cleaned up.")

        protocol.send(conn, Request('logout_success', True))

    def handle_file_content_update(self, request: Request, conn):
        file: File = request.data[0]
        changes: list[Operation] = request.data[1]
        user: User = request.data[2]

        current_content = self.database.get_file_content(user, file)

        updated_content = current_content
        for op in changes:
            updated_content = op.apply(updated_content)

        print('updated_content: ' + updated_content)

        self.database.save_file_content(user, file, updated_content)

        with self.pending_changes_lock:
            if file.file_id not in self.pending_changes:
                self.pending_changes[file.file_id] = {}

            if conn not in self.pending_changes[file.file_id]:
                self.pending_changes[file.file_id][conn] = []

            self.pending_changes[file.file_id][conn].append((file, changes))

    def handle_open_file(self, user: User, file: File, conn):
        """
        Retrieve and send the content of a file to a client, and track the user connection for future updates.

        :param user: The user requesting to open the file
        :type user: User
        :param file: The file to be opened
        :type file: File
        :param conn: The connection associated with the user
        :type conn: ssl.SSLSocket

        :return: None
        """
        content = self.database.get_file_content(user, file)

        # Track users and their connection
        if file.file_id not in self.open_files:
            self.open_files[file.file_id] = []
        # Avoid duplicates
        if not any(u.username == user.username for u, _ in self.open_files[file.file_id]):
            self.open_files[file.file_id].append((user, conn))

        protocol.send(conn, Request('file-content', [file, content]))

    def handle_update_access_table(self, request: Request, conn):
        """
                Update the access table for a file based on the provided new access list.

                :param request: Request containing the file and updated access list
                :type request: Request
                :param conn: The client connection
                :type conn: ssl.SSLSocket

                :return: None
        """
        file = request.data[0]
        updated_access = request.data[1]

        try:
            # Retrieve the current access table for the file
            for access in updated_access:
                username = access["username"]
                can_read = access["read"]
                can_write = access["write"]

                # Get the user object by username
                user = self.database.check_if_user_exists_by_username(username)
                print(user)
                if user:
                    # Update the file access for this user
                    x = self.database.change_file_access(user, file, can_read, can_write)
                    print('-' * 30)
                    print(x)
            protocol.send(conn, Request('update-access-response', True))
        except Exception as e:
            print(f"Failed to update access table: {e}")
            protocol.send(conn, Request('update-access-response', False))

    def handle_check_user_exists(self, request: Request, conn):
        """
        Check if a user exists by username and respond to the client with the result.

        :param request: Request containing the username to check
        :type request: Request
        :param conn: The client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        username = request.data
        user = self.database.check_if_user_exists_by_username(username)
        protocol.send(conn, Request('user-exists-response', user))

    def handle_get_access_list(self, request: Request, conn):
        """
        Retrieve and send the list of users who have access to a specific file.

        :param request: Request containing the file
        :type request: Request
        :param conn: The client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        file: File = request.data
        file_accesses = self.database.get_users_with_access_to_file(file)
        protocol.send(conn, Request('file-access', file_accesses))

    def handle_signup(self, request: Request, conn):
        """
        Handle user sign-up by adding them to the database and notifying the client.

        :param request: Request containing the user object
        :type request: Request
        :param conn: Client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        user: User = request.data
        already_exists = self.database.add_user(user)
        protocol.send(conn, Request('signup-success', already_exists))

    def handle_login(self, request: Request, conn):
        """
        Authenticate a user and respond to the client with success or failure, and send accessible files if successful.

        :param request: Request containing the user object
        :type request: Request
        :param conn: The client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        user: User = request.data
        success, user_id = self.database.verify_user(user)
        print('login was successful? : ' + str(success))
        user.user_id = user_id
        if success:
            user.first_name, user.last_name = self.database.get_user_full_name(user.username)
        protocol.send(conn, Request('login-success', [success, user]))
        if success:
            self.get_user_files(user, conn)

    def get_user_files(self, user: User, conn):
        """
        Retrieve and send the list of files accessible to a user.

        :param user: The user requesting their files
        :type user: User
        :param conn: Client connection to send the file list
        :type conn: ssl.SSLSocket

        :return: None
        """
        files: list[File] = self.database.get_readable_files_per_user(user)
        print(files)
        protocol.send(conn, Request("file-list", files))

    def handle_add_file(self, request, conn):
        """
        Handle the creation of a new file and set the appropriate access rights.

        :param request: Request containing the file and user
        :type request: Request
        :param conn: Client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        file = request.data[0]
        user = request.data[1]

        success_add_file = self.database.add_file(user, file, '')
        success_add_access = False

        if success_add_file:
            success_add_access = self.database.add_file_access(user, file, True, True)

        if success_add_file and success_add_access:
            protocol.send(conn, Request('add-file-success', [True, file]))
        else:
            self.database.remove_file(user.user_id, file.file_id)
            protocol.send(conn, Request('add-file-success', [False, ]))

    def handle_file_rename(self, request: Request, conn):
        """
        Rename a file in the database and notify the client of success or failure.

        :param request: Request containing the file and new name
        :type request: Request
        :param conn: Client connection
        :type conn: ssl.SSLSocket

        :return: None
        """
        file = request.data[0]
        new_name = request.data[1]
        success = self.database.rename_file(file, new_name)
        protocol.send(conn, Request('rename-file-success', success))


if __name__ == "__main__":
    server = Server()
    server.start_server()