
import socket
import ssl
from logging.config import listen
from threading import Thread

import protocol
from SQLite_database import UserDatabase
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
        for i in range(3):
            thread = Thread(target=self.listen)
            thread.start()
            self.thread_list.append(thread)


    def listen(self):
        while True:
            conn, addr = self.s_sock.accept()
            try:
                msg = protocol.recv(conn)
                self.handle_msg(msg)
            except socket.error as sock_err:
                print(sock_err)
            finally:
                self.server_socket.close()

    def handle_request(self, request: Request):
        print(f"received from client : {request}")
        if request.request_type == 'signup':
            self.handle_signup(request)
            return

    def handle_signup(self, user: User):
        pass


if __name__ == "__main__":
    server = Server()
    server.listen()
