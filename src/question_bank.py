# deserialize questions list and get the next question
# TODO: integrate with server implementation once it's ready

import json
from pathlib import Path

JSON_PATH='src/test_questions.json'

class Question:
    def __init__(self, id, question, answer):
        self.id = id
        self.question = question
        self.answer = answer

    def __iter__(self):
        yield from {
            "id": self.id,
            "question": self.question,
            "answer": self.answer
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)
    
    def to_json(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dct):
        return Question(json_dct['id'],
                        json_dct['question'],
                        json_dct['answer'])
        

def qb_from_json():
    json_str = Path(JSON_PATH).read_text()

    json_dct = json.loads(json_str)
    questions_json = json_dct["questions"]
    qb = [] 

    for q in questions_json:
        question = Question.from_json(q)
        qb.append(question)

    return qb