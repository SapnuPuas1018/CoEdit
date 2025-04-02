import socket
import ssl
import protocol
from user import User
HOST_NAME = '127.0.0.1'
PORT = 8443



class Client:
    def __init__(self):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # Allow self-signed certificate
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.my_socket = socket.socket()
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)


    def send_signup_user(self, signup_user: User):
        # Create the SSL context
        try:
            self.conn.connect((HOST_NAME, PORT))
            print('hi-------------------------------------------------')

            print('sending: ')
            print(signup_user)
            print(type(signup_user))
            protocol.send(self.conn, signup_user)
            print('hi-------------------------------------------------')
        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.conn.close()


    def send_login_user(self, login_user: User):
        # Create the SSL context

        try:
            self.conn.connect((HOST_NAME, PORT))
            print('hi-------------------------------------------------')

            print('sending: ')
            print(login_user)
            print(type(login_user))
            protocol.send(self.conn, login_user)
            print('hi-------------------------------------------------')
        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.conn.close()


    def add_file(self, file_name):
        protocol.send(self.conn, '', file_name)
        # protocol.recv()


if __name__ == '__main__':
    # Create a client instance
    pass
