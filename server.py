import socket
import ssl
from SQLite_database import UserDatabase
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
        self.server_socket.bind((IP_ADDR, PORT))
        self.server_socket.listen(QUEUE_LEN)
        self.thread_list = []  # List of threads handling clients
        self.database = UserDatabase()



    def start_server(self):
        try:
            print(f"Server listening on {IP_ADDR}:{PORT}")
            while True:
                client_socket, addr = self.server_socket.accept()  # Accept first
                print('Received a connection')

                # Wrap the accepted client socket with SSL
                ssl_client_socket = self.context.wrap_socket(client_socket, server_side=True)

                try:
                    thread = Thread(target=identification, args=(self, ssl_client_socket, addr))
                    thread.start()
                    self.thread_list.append(thread)
                except socket.error as sock_err:
                    print(f"Error in thread: {sock_err}")
                # No need to close client_socket here, as it's passed to a thread

        except socket.error as sock_err:
            print(f"Server error: {sock_err}")

        finally:
            self.database.close()
            self.server_socket.close()




def identification(self, client_socket, addr):
    try:
        print('iiiiiiiiiiiiiiiiiiiii')
        signup_result = protocol.recv(client_socket, 'REGISTER')
        print(f"Received from {addr}: {signup_result}")
        already_exists, message = self.database.add_user(signup_result)
        print(message)

        send_file_names(self, client_socket, signup_result)

    except socket.error as sock_err:
        print(f"Socket error at handle_connection: {sock_err}")

    finally:
        client_socket.close()  # Make sure to close the connection


def send_file_names(self, client_socket, user):
    file_names = self.database.get_files(user)
    print(file_names)
    protocol.send(client_socket,'REGISTER', file_names)


def add_file(self, client_socket, user):
    file_name = protocol.recv(client_socket, '')
    already_exists, message = self.database.add_file(user, file_name, '')
    print(message)


def send_file_context(self, client_socket, user, file_name):
    pass


if __name__ == '__main__':
    server = Server()
    server.start_server()
