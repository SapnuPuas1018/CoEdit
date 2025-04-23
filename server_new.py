
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
            thread = Thread(target=self.listen, args=(conn, ))
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
            conn.close()

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

    def handle_signup(self, request: Request, conn):
        user: User = request.data
        print(type(user))
        print(user)
        already_exists, message = self.database.add_user(user)
        protocol.send(conn, Request('signup-success', already_exists))
        print(message)

    def handle_login(self, request: Request, conn):
        user: User = request.data
        success = self.database.verify_user(user)
        print('login was successful? : ' + str(success))
        protocol.send(conn, Request('login-success', [success, user]))
        if success:
            self.get_user_files(user, conn)


    def get_user_files(self, user: User, conn):
        files: list[File] = self.database.get_readable_files_per_user(user)
        files_user_can_read = []
        for file in files:
            if self.database.can_user_read_file(user, file):
                files_user_can_read.append(file)
                files.remove(file)


        protocol.send(conn, Request("file-list", files_user_can_read))


    def handle_add_file(self, request, conn):
        file = request.data[0]
        user = request.data[1]
        #   add file access to owner/user
        self.database.add_file(user, file, '')
        self.database.add_file_access(user, file, True, True)



        

if __name__ == "__main__":
    server = Server()
    server.start_server()
