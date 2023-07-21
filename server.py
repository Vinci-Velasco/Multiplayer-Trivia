import socket
import threading
from queue import Queue

HOST = "127.0.0.1"
PORT = 7070

# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed
    with client_socket:
        while True:
            message = client_socket.recv(BUFFER_SIZE).decode("utf8")
            print(f"Recieved message from {addr}")
            message_queue.put(message)

# Custom thread class that creates new threads once connections come in
class Recieve_Connection_Thread(threading.Thread):
    def __init__(self, server, message_queue):
        super().__init__()
        self.server = server
        self.message_queue = message_queue
        self.stop_connections = False

    # Listens to connections and creates new threads. Closes once max connections achieved
    # or stop_connections is set to True (via the stop() method)
    def run(self):
        connections = 0
        MAX_CONNECTIONS = 5

        while connections < MAX_CONNECTIONS:
            print(f"Listening for connections ({connections}/{MAX_CONNECTIONS})...")
            client_socket, addr = self.server.accept()

            # terminate thread if stop_connections set to True
            if self.stop_connections:
                break

            # otherwise create new thread for connection
            client_sockets.append(client_socket)
            thread = threading.Thread(
                target=listening_thread, args=(client_socket, addr, self.message_queue))
            thread.start()
            connections += 1

        print(f"Done with connections ({connections}/{MAX_CONNECTIONS})")

    # Stop the thread by changing the stop_connections cond to True and unblocking the
    # server.accept() call. This is safer than killing the thread as it can terminate properly
    def stop(self):
        self.stop_connections = True
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, PORT))


if __name__ == "__main__":
    # setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM = TCP
    server.bind((HOST, PORT))
    server.listen()

    # data structures to hold client sockets and message queue so main can communicate
    # with listening threads and vice versa
    client_sockets = []
    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

    # lobby loop
    host_voted = False
    all_ready = False
    while not (all_ready and host_voted):
        message = message_queue.get()
        print(message)

        # application layer protocol for lobby (parse tokens)
        # ...

        for client in client_sockets:
            # send data to all clients
            pass

    # close ability to connect
    recieve_connections_thread.stop()
    recieve_connections_thread.join()

    # send info to clients that main game has started
    # ...

    # main game loop
    game_loop = True
    while game_loop:
         message = message_queue.get()

         # application layer protocol for game loop (parse tokens)
         # ...

         for client in client_sockets:
             # send data to all clients
             pass