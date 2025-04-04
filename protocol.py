
import socket
import ssl
import pickle
from asyncio.subprocess import Process

from user import User

def send(sock, data):
    serialized_data = pickle.dumps(data)
    length = len(serialized_data)
    data_to_send = str(length).encode() + '!'.encode() + serialized_data
    print(f'sending : {data_to_send}, type {type(data_to_send)}')
    sock.send(data_to_send)
    print('stam mashehu')



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
