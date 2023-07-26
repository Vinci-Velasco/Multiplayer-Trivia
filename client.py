# PLACEHOLDER - just for testing


import socket
import time


HOST = "127.0.0.1"
PORT = 7070


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
    my_socket.connect((HOST, PORT))


    index = 0
    while True:
        time.sleep(3)
        my_socket.send("hello".encode("utf8"))


        BUFFER_SIZE = 1024
   
        data = my_socket.recv(BUFFER_SIZE).decode("utf8")
        print(f"Recived: {data}")
     

        #on 5th loop client can choose to ready up (only here for testing change as needed)
        if(index == 5):
            userTestInput = input("would you like to ready up? ('y' or 'n'): ")


            if(userTestInput == "y"):
                my_socket.send("Ready_Up-3-some type of data".encode("utf8"))


        index += 1