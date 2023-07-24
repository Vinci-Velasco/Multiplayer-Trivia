class Tokens:
    Answer = "Answer"
    Begin_Vote = "Begin_Vote"
    Buzzing = "Buzzing"
    Host_Choice = "Host_Choice"
    Message = "Message"
    Player_Join = "Player_Join"
    Player_Number = "Player_Number"
    Ready_Up = "Ready_Up"
    Vote_Host = "Vote_Host"


def parse_message(message):
    token = message.split(" ")[0]
    data = ' '.join(message.split(" ")[1:])

    return token, data


def send_all(sockets, message):
    for s in sockets:
        s.send(message.encode("utf8"))


def send(socket, message):
	socket.send(message.encode("utf8"))