import random

#### Application logic for Lobby
# use list of Players, not Client 
MIN_PLAYERS = 3

#### Get current state of Lobby
def get_state(players, last_state):
    nplayers = len(players)

    #### Waiting for more players to join before we can start the game
    if nplayers < MIN_PLAYERS:
        return "WAIT"
    
    #### Check last game state
    if last_state == "VOTE":
        # Check total amount of votes
        total_votes = get_total_votes(players)
        
        if total_votes < nplayers:
            return "VOTE"
        else: # After all players have voted, next state is to choose the host
            return "FIND_HOST"
    
    elif last_state == "FIND_HOST":
        # Server needs to change the state to HOST_FOUND manually
        return "FIND_HOST"
    
    elif last_state == "HOST_FOUND":
        return "READY_UP"
    
    elif last_state == "READY_UP":
        # Check total amount of ready ups
        total_ready = 0
        for p in players:
            if p.readied_up:
                total_votes += 1

        if total_ready < nplayers:
            return "READY_UP"
        else: # After all players have readied up, start the game
            return "START_GAME"
        
    return "INVALID_STATE"
        
        
def calculate_host(players):
    host = None

    for p in players:
        if not host or (p.votes > host.votes):
            host = p
        # If there's a tie, pick betewen them randomly
        elif p.votes == host.votes:
            host = random.choice(p, host)
    
    return host

def get_total_votes(players):
    total_votes = 0
    for p in players:
        if p.already_voted:
            total_votes +=1

    return total_votes