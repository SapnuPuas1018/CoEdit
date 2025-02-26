import socket
import ssl
import protocol

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
            conn, addr = s_sock.accept()
            try:
                msg = protocol.recv(conn)
                if msg != '':
                    while msg != EXIT_CMD:
                        print('received ' + msg)
                        protocol.send(conn, MSG)
                        msg = protocol.recv(conn)
                    protocol.send(conn, EXIT_RES)
                    print('exiting')
            except socket.error as sock_err:
                print(sock_err)
            finally:
                conn.close()
        except socket.error as sock_err:
            print(sock_err)
        finally:
            self.server_socket.close()


if __name__ == '__main__':
    server = Server()
    server.start_server()
