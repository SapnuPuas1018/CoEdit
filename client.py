import queue
import socket
import ssl
import threading

import protocol
from request import Request

HOST_NAME = '127.0.0.1'
PORT = 8468


class Client:
    def __init__(self):
        self.running = True
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)

        self.response_queue = queue.Queue()
        # self.my_user

    def connect(self):
        try:
            self.conn.connect((HOST_NAME, PORT))
            threading.Thread(target=self.listen, daemon=True).start()
        except Exception as e:
            print('failed to connect: ' + str(e))

    def listen(self):
        while self.running:
            try:
                response = protocol.recv(self.conn)
                self.response_queue.put(response)
                print(f'received a msg from {self.conn}')
            except Exception as e:
                print(f"Error in listen: {e}")
                break

    def stop(self):
        self.running = False
        self.conn.close()

    def send_request(self, request: Request):
        try:
            protocol.send(self.conn, request)
        except socket.error as sock_err:
            print(sock_err)

    def get_response_nowait(self):
        """Non-blocking check for new messages."""
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None



if __name__ == "__main__":
    client = Client()
