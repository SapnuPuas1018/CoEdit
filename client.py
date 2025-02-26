import socket
import ssl
import protocol

HOST_NAME = '127.0.0.1'
PORT = 8443
EXIT_CMD = 'by by'
USER_INPUT = 'please enter a command'



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
            msg = input(USER_INPUT)
            while True:
                protocol.send(self.conn, msg)
                answer = protocol.recv(self.conn)
                print(answer)
                if answer == '' or answer == EXIT_CMD:
                    break
                msg = input(USER_INPUT)
            print('exiting')
        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.conn.close()

def main():
    """
    Creates a secure connection with the server, receives commands, sends them to the server, and receives a response
    from the server.
    Exits when it receives the 'by by' response.
    :return: None
    """
    # Create the SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Allow self-signed certificate
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    my_socket = socket.socket()
    conn = context.wrap_socket(my_socket, server_hostname=HOST_NAME)
    try:
        conn.connect((HOST_NAME, PORT))
        msg = input(USER_INPUT)
        while True:
            protocol.send(conn, msg)
            answer = protocol.recv(conn)
            print(answer)
            if answer == '' or answer == EXIT_CMD:
                break
            msg = input(USER_INPUT)
        print('exiting')
    except socket.error as sock_err:
        print(sock_err)
    finally:
        conn.close()


if __name__ == '__main__':
    # Create a client instance
    client = Client()
    client.start_client()