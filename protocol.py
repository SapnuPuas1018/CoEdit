
import socket
import ssl
import pickle
from asyncio.subprocess import Process

from user import User

# def int_to_bytes(number: int) -> bytes:
#     return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)
#
# def int_from_bytes(binary_data: bytes) -> int:
#     return int.from_bytes(binary_data, byteorder='big', signed=True)
#
# def send(connected_socket, msg):
#     """
#     Send a message over the connected socket.
#
#     :param connected_socket: The connected socket to send the message through.
#     :type connected_socket: socket.socket
#
#     :param msg: The message to be sent.
#     :type msg: str
#
#     :return: None
#     :rtype: None
#     """
#     data = pickle.dumps(msg)
#     # Check if the last character of the 'msg' string is a space
#
#     # Convert the length of the 'msg' string to hexadecimal representation, excluding the '0x' prefix
#     msg = int_to_bytes(len(data)) + b'!' + data
#     print(msg)
#     # Encode the modified 'msg' string and send it through the 'connected_socket'
#     connected_socket.send(msg)


# def recv(connected_socket):
#     """
#     Receive a message from the connected socket.
#
#     :param connected_socket: The connected socket to receive the message from.
#     :type connected_socket: socket.socket
#
#     :return: A list containing the split components of the received message.
#     :rtype: list[str]
#     """
#     # Receive the length of the message in hexadecimal
#     print('receiving')
#     length_hex = b''
#     tmp = b''
#     while tmp != b'!':
#         print(length_hex)
#         length_hex += tmp
#         tmp = connected_socket.recv(1)
#
#     # Convert the length to an integer
#     length = int_from_bytes(length_hex)
#
#     # Receive the message until the expected length is reached
#     received_msg = b''
#     while len(received_msg) < length:
#         received_msg += connected_socket.recv(1)
#     data = pickle.loads(received_msg)
#     # Split the received message using '!!' as the separator
#     return data

def send(sock, data):
    serialized_data = pickle.dumps(data)
    length = len(serialized_data)
    data_to_send = str(length).encode() + '!'.encode() + serialized_data
    print(f'sending : {data_to_send}, type {type(data_to_send)}')
    sock.send(data_to_send)



def recv(sock):
    length_data = b''
    # print('start length_data')
    while b'!' not in length_data:
        length_data += sock.recv(1)
        # print(length_data.decode())
    # print('found !')
    length = int(length_data[:-1])  # Remove '!' and convert to int

    # Receive the full message
    received_data = b''
    while len(received_data) < length:
        chunk = sock.recv(length - len(received_data))
        if not chunk:
            raise ConnectionError("Socket connection closed")
        received_data += chunk

    return pickle.loads(received_data)

if __name__ == '__main__':
    # Testing the send and recv functions using a socketpair
    parent_sock, child_sock = socket.socketpair()

    test_data = User('','','jd123', 'securepassword123')

    send(parent_sock,test_data)
    received_data = recv(child_sock)

    print(type(received_data))
    print(type(test_data))

    print(received_data)
    print(test_data)
    if received_data == test_data:
        print('passed')
    else:
        print('failed')
    # assert received_data == test_data, "Data integrity check failed!"
    # print("Test passed: Data integrity verified.")

    parent_sock.close()
    child_sock.close()
