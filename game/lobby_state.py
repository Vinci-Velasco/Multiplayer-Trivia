import random

#### Application logic for Lobby
# use list of Players, not Client
MIN_PLAYERS = 5
init_state = "WAIT"

class Lobby():
    def __init__(self, player_list=[]):
        self.player_list = player_list
        self.current_state = init_state
        self.last_state = init_state

        self.host = None
    
    def update_state(self, new_state):
        self.last_state = self.current_state
        self.current_state = new_state
        return new_state
    
    def update_players(self, player_list):
        self.player_list = player_list
    
    #### Get current state of Lobby
    def get_state(self):
        state = self.current_state
        player_list = self.player_list
        num_players = len(player_list)

        if state == "START_GAME" or self.last_state == "SENDING_QUESTION":
            return "START_GAME"
    
        ## Wait for minimum number of players to join
        elif state == "WAIT":
            if num_players < MIN_PLAYERS:
                #TODO: check num **connected** players
                return "WAIT"
            elif(num_players >= MIN_PLAYERS):
                return self.update_state("VOTE")
    
        ## Start Host Voting phase
        elif state == "VOTE":
            total_votes = self.get_total_votes(player_list)
            if total_votes < num_players:
                return self.update_state("VOTE")
            else:
                return self.update_state("FIND_HOST")
    
        ##  After voting complete, next state is to Find Host
        # Server needs to change the state to HOST_FOUND manually once it calculates the host and broadcasts choice to all clients
        elif state == "FIND_HOST":
            return "FIND_HOST"
    
        elif state == "HOST_FOUND":
            return self.update_state("READY_UP")
    
        ## Start READY_UP phase
        elif state == "READY_UP":
            total_ready = self.get_total_ready(player_list)

            if total_ready < num_players:
                return self.update_state("READY_UP")

            # After all players have readied up, start the game
            else: 
                return self.update_state("START_GAME")
        
        return "INVALID_STATE"
    
    def state_changed(self):
        return not self.last_state == self.current_state
       
    def calculate_host(self):
        if self.host != None:
            return self.host
        else:
            host = None
            player_list = self.player_list

            for p in player_list:
                if(host == None):
                    host = p
                    continue
                if (p != host and (p.votes > host.votes)):
                    host = p
                # If there's a tie, pick betewen them randomly
                elif p.votes == host.votes:
                    tempList = []
                    tempList.append(p)
                    tempList.append(host)
                    host = random.choice(tempList)
                    tempList.clear()
            self.host = host
            return host
    
    def host_found(self):
        return not (self.host == None)

    def get_total_votes(self, player_list):
        total_votes = 0
        for p in player_list:
            if p.already_voted:
                total_votes +=1

        return total_votes
    
    def get_total_ready(self, player_list):
        total_ready = 0
        for p in player_list:
            if p.readied_up:
                total_ready += 1

        return total_ready
