import queue
import socket
import ssl
import threading
import time
from ssl import SSLContext
from typing import Any

import protocol  # Assuming you have a custom protocol module
from request import Request
from user import User

HOST_NAME = '127.0.0.1'
PORT = 8468


class Client:
    def __init__(self, gui_manager):
        self.running = True
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.check_hostname = False  # Allow self-signed certificate
        self.context.verify_mode = ssl.CERT_NONE
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)

        self.response_queue = queue.Queue()

        self.gui_manager = gui_manager
    def connect(self):
        try:
            self.conn.connect((HOST_NAME, PORT))
            threading.Thread(target=self.listen, daemon=True).start()

        except Exception as e:
            print('failed to connect: ' + str(e))


    def stop(self):
        self.running = False
        self.conn.close()
        print("Stopping client thread...")

    def listen(self):
        while self.running:
            try:
                self.response_queue.put(protocol.recv(self.conn))
                self.gui_manager.change_state()
                print(f'received a msg from {self.conn}')
            except Exception as e:
                break

    def get_response(self, timeout=5) -> Request | None:
        """Fetch a response from the queue (waits up to `timeout` seconds)."""
        try:
            return self.response_queue.get(timeout=timeout)  # Waits for response
        except queue.Empty:
            return None

    def send_request(self, request: Request):
        print('-' * 30)
        try:
            print(self.conn)
            protocol.send(self.conn, request)

        except socket.error as sock_err:
            print(sock_err)


if __name__ == "__main__":
    client = Client()
    client.send_request(Request('signup', User('yuval', 'hayun', 'eee', '123')))
