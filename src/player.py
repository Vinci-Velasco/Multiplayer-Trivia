class Player():
    def __init__(self, id, is_me=False):
        self.id = id

        # initial instance values
        self.votes = 0
        self.score = 0
        self.is_host = False
        self.is_me = is_me
        self.already_voted = False
        self.readied_up = False
        self.disconnected = False
        self.received_question = False
        self.received_host_choice = False
        self.has_lock = False

    def increaseScore(self):
        self.score += 1

    def getScore(self):
        return self.score
