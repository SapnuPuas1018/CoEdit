import socket
import ssl
import threading
from typing import Any

import protocol  # Assuming you have a custom protocol module
from request import Request
from user import User

HOST_NAME = "127.0.0.1"
PORT = 8468


class Client:
    def __init__(self):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.check_hostname = False  # Allow self-signed certificate
        self.context.verify_mode = ssl.CERT_NONE
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)

    def send_request(self, request: Request):
        print('-' * 30)
        try:
            if request.request_type == 'login' or request.request_type == 'signup':
                self.conn.connect((HOST_NAME, PORT))
                protocol.send(self.conn, request)

        except socket.error as sock_err:
            print(sock_err)

        finally:
            self.conn.close()

if __name__ == "__main__":
    client = Client()
    client.send_request(Request('signup', User('yuval','hayun', 'eee', '123')))
