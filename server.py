import socket
import ssl
import threading

import protocol
from threading import Thread
IP_ADDR = '0.0.0.0'
PORT = 8443
QUEUE_LEN = 1
CERT_FILE = 'certificate.crt'
KEY_FILE = 'privateKey.key'
MSG = 'have a nice day'
EXIT_CMD = 'exit'
EXIT_RES = 'by by'


class Server:
    def __init__(self):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(CERT_FILE, KEY_FILE)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_list = []  # List of threads handling clients

    def start_server(self):
        try:
            self.server_socket.bind((IP_ADDR, PORT))
            self.server_socket.listen(QUEUE_LEN)
            s_sock = self.context.wrap_socket(self.server_socket, server_side=True)
            while True:
                client_socket, addr = s_sock.accept()
                print('received a connection')
                try:
                    thread = Thread(target=handle_connection, args=(client_socket, addr))
                    thread.start()
                    self.thread_list.append(thread)
                except socket.error as sock_err:
                    print(sock_err)
                finally:
                    client_socket.close()
        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.server_socket.close()




def handle_connection(client_socket, addr):
    pass


def check_user_in_database():
    pass


def send_file_names():
    pass


def send_file_context():
    pass


if __name__ == '__main__':
    server = Server()
    server.start_server()
