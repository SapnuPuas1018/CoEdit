import socket
import ssl
import protocol
from login import AuthApp
from user import User
HOST_NAME = '127.0.0.1'
PORT = 8443



class Client:
    def __init__(self):
        pass


    def start_client(self):
        # Create the SSL context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # Allow self-signed certificate
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.my_socket = socket.socket()
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)
        try:
            self.conn.connect((HOST_NAME, PORT))
            print('hi-------------------------------------------------')
            signup_result = AuthApp().mainloop()

            protocol.send(self.conn, 'REGISTER', signup_result)
            print('hi-------------------------------------------------')
            print('sending: ')
            print(signup_result)



        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.conn.close()


if __name__ == '__main__':
    # Create a client instance
    client = Client()
    client.start_client()
