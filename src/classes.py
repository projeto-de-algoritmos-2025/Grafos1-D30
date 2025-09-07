import uuid

class course():
    def __init__(self, name):
        self.id = uuid.uuid4().hex
        self.name = name
        self.subjects = []

    def create_subject(self, name):
        disc = subject(name)
        self.subjects.append(disc)

    def data_list(self): # Gera uma lista contendo as informações do objeto (serialização)
        subjects = {}
        for s in self.subjects:
            subjects[s.name] = s.prereqs
        db_list = {
            'id': self.id,
            'name': self.name,
            'subjects': subjects
        }
        return db_list


class subject():
    def __init__(self, name):
        self.name = name
        self.prereqs = []
    
    def add_prereq(self, subject):
        self.prereqs.append(subject)