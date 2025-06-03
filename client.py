import queue
import socket
import ssl
import threading

import protocol
from request import Request

HOST_NAME = '127.0.0.1'
PORT = 8468


class Client:
    """
    Handles the SSL connection to the server, manages sending requests,
    receiving responses, and maintaining a client-side message queue.
    """
    def __init__(self):
        """
        Initializes the Client instance by setting up an SSL context,
        creating a socket, wrapping it with SSL, and preparing a queue
        to store server responses.
        """
        self.running = True
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.context.wrap_socket(self.my_socket, server_hostname=HOST_NAME)

        self.response_queue = queue.Queue()

    def connect(self):
        """
        Connects the client to the server over SSL and starts a background
        thread to listen for incoming responses.

        :raises Exception: If the connection fails.
        """
        try:
            self.conn.connect((HOST_NAME, PORT))
            threading.Thread(target=self.listen, daemon=True).start()
        except Exception as e:
            print('failed to connect: ' + str(e))
            quit()

    def listen(self):
        """
        Listens for incoming messages from the server in a loop and stores them
        in the response queue. Runs in a separate thread.

        This method handles exceptions gracefully and stops on errors.
        """
        while self.running:
            try:
                response = protocol.recv(self.conn)
                self.response_queue.put(response)
                print(f'received a msg from {self.conn}')
            except Exception as e:
                print(f"Error in listen: {e}")
                break

    def send_request(self, request: Request):
        """
        Sends a request object to the server using the custom protocol.

        :param request: The request object to send.
        :type request: Request
        :raises socket.error: If a socket-level error occurs while sending.
        """
        try:
            protocol.send(self.conn, request)
        except socket.error as sock_err:
            print(sock_err)

    def get_response_nowait(self):
        """
        Retrieves a response from the queue without blocking.

        :return: The response object if available, otherwise None.
        :rtype: Any or None
        """
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):

        self.running = False
        self.conn.close()

    def disconnect(self):
        try:
            if self.conn:
                self.stop()
                print("Disconnected from server.")
        except Exception as e:
            print(f"Error during disconnect: {e}")


if __name__ == "__main__":
    client = Client()
