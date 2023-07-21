# PLACEHOLDER - just for testing

import socket
import time

HOST = "127.0.0.1"
PORT = 7070

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
    my_socket.connect((HOST, PORT))

    while True:
        time.sleep(5)
        my_socket.send("hello".encode("utf8"))

        BUFFER_SIZE = 1024
        data = my_socket.recv(BUFFER_SIZE).decode("utf8")
        print(f"Recived: {data}")