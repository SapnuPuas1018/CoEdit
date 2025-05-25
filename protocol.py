
import socket
import ssl
import pickle
from asyncio.subprocess import Process

from user import User

def send(sock, data):
    """
    Sends serialized data over a socket with a prefixed length header.

    :param sock: The socket object through which the data is sent
    :type sock: socket.socket

    :param data: The Python object to be serialized and sent
    :type data: Any

    :return: None
    :rtype: None
    """

    serialized_data = pickle.dumps(data)
    length = len(serialized_data)
    data_to_send = str(length).encode() + '!'.encode() + serialized_data
    sock.send(data_to_send)



def recv(sock):
    """
    Receives data from a socket, reconstructs the message from the byte stream, and deserializes it.

    :param sock: The socket object from which data is received
    :type sock: socket.socket

    :return: The deserialized Python object received from the socket
    :rtype: Any
    """
    length_data = b''
    while b'!' not in length_data:
        length_data += sock.recv(1)
    length = int(length_data[:-1])  # Remove '!' and convert to int

    # Receive the full message
    received_data = b''
    while len(received_data) < length:
        chunk = sock.recv(length - len(received_data))
        if not chunk:
            raise ConnectionError("Socket connection closed")
        received_data += chunk

    return pickle.loads(received_data)
