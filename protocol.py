"""
author - Yuval Hayun
date   - 12/12/23
"""

import socket
import ssl
import pickle
from user import User


def send(sock, command, data):
    if command == 'REGISTER':
        serialized_data = pickle.dumps(data)
        length = len(serialized_data)
        data_to_send = str(length).encode() + '!'.encode() + serialized_data
        sock.send(data_to_send)
    else:
        msg = data.strip()
        msg = str(len(msg)) + '!' + ' '.join(msg.split())

        # Encode the modified 'msg' string and send it through the 'connected_socket'
        sock.send(msg.encode())


def recv(sock, command):
    length = ''
    while '!' not in length:
        length += sock.recv(1).decode()  # Read until '!' is found
    length = length[:-1]  # Remove '!' from length
    length = int(length)  # Convert length to integer

    if command == 'REGISTER':
        # Receive the message until the expected length is reached
        received_data = b''
        while len(received_data) < length:
            received_data += sock.recv(length - len(received_data))

        print(f'received_data: {received_data}')
        received_data = pickle.loads(received_data)
    else:
        # Receive the message until the expected length is reached
        received_data = ''
        while len(received_data) < length:
            received_data += sock.recv(length - len(received_data)).decode()

        print(f'received_data: {received_data}')
    return received_data


if __name__ == '__main__':
    HOST_NAME = '127.0.0.1'
    PORT = 8443
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    my_socket = socket.socket()
    conn = context.wrap_socket(my_socket, server_hostname=HOST_NAME)
    try:
        conn.connect((HOST_NAME, PORT))
        signup_result = User('Paty', 'Amiga', 'PT', 'idk')
        send(conn, 'REGISTER', signup_result)

        file_names = recv(conn, 'REGISTER')
        print('file_names: ')
        print(file_names)


    except socket.error as sock_err:
        print(sock_err)
