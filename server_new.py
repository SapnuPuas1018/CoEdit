import socket
import ssl
from threading import Thread

import protocol
from SQLite_database import UserDatabase
from file import File
from request import Request
from user import User

IP_ADDR = '0.0.0.0'
PORT = 8468
QUEUE_LEN = 1
CERT_FILE = 'certificate.crt'
KEY_FILE = 'privateKey.key'


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

    def start_server(self):
        while True:
            conn, addr = self.s_sock.accept()
            print(f'received a connection from {conn}, {addr}')
            thread = Thread(target=self.listen, args=(conn,))
            thread.start()
            self.thread_list.append(thread)

    def listen(self, conn):
        try:
            while True:
                msg = protocol.recv(conn)
                print(f'received a msg from {conn}, msg {msg}')
                self.handle_request(msg, conn)
        except socket.error as sock_err:
            print(sock_err)
        finally:
            conn.close()  # todo check if it actually closes the connection
            self.cleanup_connection(conn)

    def cleanup_connection(self, conn):
        for file_id in list(self.open_files):
            self.open_files[file_id] = [(u, c) for u, c in self.open_files[file_id] if c != conn]
            if not self.open_files[file_id]:
                del self.open_files[file_id]

    def handle_request(self, request: Request, conn):
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
            self.open_file(request.data[0], request.data[1], conn)
        elif request.request_type == 'get-access-list':
            self.handle_get_access_list(request, conn)
        elif request.request_type == 'check-user-exists':
            self.handle_check_user_exists(request, conn)
        elif request.request_type == 'update-access-table':
            self.handle_update_access_table(request, conn)
        elif request.request_type == 'file-content-update':
            self.handle_file_content_update(request, conn)
        # todo: maybe maybe, optional, to add a refresh text button in the editor screen
        # elif request.request_type == 'refresh-text':
        #     pass

    def handle_file_content_update(self, request: Request, sender_conn):
        file: File = request.data[0]
        changes: list[dict] = request.data[1]
        user: User = request.data[2]

        # Get current content
        current_content = self.database.get_file_content(user, file)

        # Apply changes
        result = self.apply_changes(current_content, changes)
        updated_content = result["content"]
        changes = result["changes"]  # This might be unchanged, but safe to reassign

        # Save new content to DB, also checks if I have permission to write
        self.database.save_file_content(user, file, updated_content)

        # Broadcast to other clients
        for user, conn in self.open_files.get(file.file_id, []):
            if conn != sender_conn:
                try:
                    protocol.send(conn, Request('file-content-update', [file, changes]))
                except Exception as e:
                    print(f"Error sending update to {user.username}: {e}")

    def apply_changes(self, original: str, changes: list[dict]) -> dict:
        lines = original.splitlines(keepends=True)
        for change in changes:
            line = change["line"]
            char = change["char"]
            if line >= len(lines): continue
            line_content = lines[line]
            if "delete" in change:
                del_text = change["delete"]
                lines[line] = line_content[:char] + line_content[char + len(del_text):]
            if "insert" in change:
                ins_text = change["insert"]
                lines[line] = line_content[:char] + ins_text + line_content[char:]
        return {"content": ''.join(lines), "changes": changes}

    # def handle_edit_file(self, request: Request, sender_conn):
    #     file: File = request.data[0]
    #     new_content: str = request.data[1]
    #
    #     # Save the new content (if needed)
    #     self.database.update_file_content(file, new_content)
    #
    #     # Notify all other clients with the file open
    #     if file.file_id in self.open_files:
    #         for user, conn in self.open_files[file.file_id]:
    #             if conn != sender_conn:  # Don't send the update back to the sender
    #                 try:
    #                     protocol.send(conn, Request('file-updated', [file, new_content]))
    #                 except Exception as e:
    #                     print(f"Failed to notify {user.username}: {e}")

    def open_file(self,  user: User , file: File, conn):
        content = self.database.get_file_content(user, file)

        # Track users and their connection
        if file.file_id not in self.open_files:
            self.open_files[file.file_id] = []
        # Avoid duplicates
        if not any(u.username == user.username for u, _ in self.open_files[file.file_id]):
            self.open_files[file.file_id].append((user, conn))
            
        protocol.send(conn, Request('file-content', [file, content]))

    def handle_update_access_table(self, request: Request, conn):
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
                    print('-'*30)
                    print(x)
            protocol.send(conn, Request('update-access-response', True))
        except Exception as e:
            print(f"Failed to update access table: {e}")
            protocol.send(conn, Request('update-access-response', False))

    def handle_check_user_exists(self, request: Request, conn):
        username = request.data
        user = self.database.check_if_user_exists_by_username(username) # returns None if not found
        protocol.send(conn, Request('user-exists-response', user))

    def handle_get_access_list(self, request: Request, conn):
        file: File = request.data
        file_accesses = self.database.get_users_with_access_to_file(file)
        protocol.send(conn, Request('file-access', file_accesses))

    def handle_signup(self, request: Request, conn):
        user: User = request.data
        print(type(user))
        print(user)
        already_exists = self.database.add_user(user)
        protocol.send(conn, Request('signup-success', already_exists))

    def handle_login(self, request: Request, conn):
        user: User = request.data
        success, user_id = self.database.verify_user(user)
        print('login was successful? : ' + str(success))
        user.user_id = user_id
        protocol.send(conn, Request('login-success', [success, user]))
        if success:
            self.get_user_files(user, conn)

    def get_user_files(self, user: User, conn):
        files: list[File] = self.database.get_readable_files_per_user(user)
        print(files)
        protocol.send(conn, Request("file-list", files))

    def handle_add_file(self, request, conn):
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
        file = request.data[0]
        new_name = request.data[1]
        success = self.database.rename_file(file, new_name)
        protocol.send(conn, Request('rename-file-success', success))


if __name__ == "__main__":
    server = Server()
    server.start_server()