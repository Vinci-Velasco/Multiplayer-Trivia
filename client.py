#### use client.py to communicate directly with the server via passed-in sockets

import socket
import time
import pickle
import traceback

HOST = "127.0.0.1"
PORT = 7070

#### Data Strings need to be decoded with utf8
def req_data_string(s, string):
    BUFFER_SIZE = 1024
    s.send(f"Req_Data-String-{string}".encode('utf8'))
    
    string = s.recv(BUFFER_SIZE).decode('utf8')
    return string

#### Data Objects need to be serialized/deserialized with pickle
def req_data_object(s, object):
    BUFFER_SIZE = 1024
    s.send(f"Req_Data-Object-{object}".encode('utf8'))

    object_data = s.recv(BUFFER_SIZE)
    object = pickle.loads(object_data)
    return object

def send_ack(s, data):
    s.send(f"ACK-{data}".encode('utf8'))

def update_this_player(s):
    # send update of this players data to server
    pass

def update_lobby(s):
    # Ask server for current Lobby State, e.g. if we are in Voting phase or Ready Up phase...
    current_phase = req_data_string(s, "lobby_state")
    if current_phase == "VOTE":
        # get vote data
        # send ack
        pass
    elif current_phase == "FIND_HOST":
        # get host data
        # send ack
        pass
    elif current_phase == "READY_UP":
        # get ready_up data
        # send ack
        pass
    elif current_phase == "START_GAME":
        # get data to start the game
        # send ack
        pass

def ready_up_test():
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


if __name__ == '__main__':
    ready_up_test()