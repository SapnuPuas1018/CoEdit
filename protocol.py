"""
author - Yuval Hayun
date   - 12/12/23
"""

import socket
import ssl

from user import User
import pickle



def send(connected_socket, command, data):
    """
    Sends a message to the connected socket. The message is formatted to include its length
    as a prefix followed by an exclamation mark (`!`), and spaces in the message are normalized.

    :param connected_socket: The socket through which the message is sent
    :type connected_socket: socket.socket
    :param msg: The message to send
    :type msg: str
    :return: None
    :rtype: None
    """

    if command == 'REGISTER':
        serialized_user = pickle.dumps(data)
        data_to_send = str(len(serialized_user)) + '!' + str(serialized_user)

        connected_socket.send(data_to_send.encode())
        print(f'sent: {data_to_send}')

    else:
        msg = data.strip()
        msg = str(len(msg)) + '!' + ' '.join(msg.split())

        # Encode the modified 'msg' string and send it through the 'connected_socket'
        connected_socket.send(msg.encode())


def recv(connected_socket):
    """
    Receives a message from the connected socket. It first reads the length prefix, then receives
    the actual message until the expected length is met.

    :param connected_socket: The socket from which the message is received
    :type connected_socket: socket.socket
    :return: The received message
    :rtype: str
    """
    length = ''
    while '!' not in length:
        length += connected_socket.recv(1).decode()  # Read until '!' is found
    length = length[:-1]  # Remove '!' from length

    length = int(length)  # Convert length to integer

    # Receive the message until the expected length is reached
    received_msg = ''
    while len(received_msg) < length:
        received_msg += connected_socket.recv(length - len(received_msg)).decode()

    return received_msg

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
        signup_result = User('Yuval', 'Hayun', 'Sapnu Puas', 'very_secured_password1234')
        send(conn, 'REGISTER', signup_result)



    except socket.error as sock_err:
        print(sock_err)

