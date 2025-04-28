
import socket
import ssl
import pickle
from asyncio.subprocess import Process

from user import User

def send(sock, data):
    serialized_data = pickle.dumps(data)
    length = len(serialized_data)
    data_to_send = str(length).encode() + '!'.encode() + serialized_data
    sock.send(data_to_send)



def recv(sock):
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
