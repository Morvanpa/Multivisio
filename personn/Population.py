import Personn

class Population():
    def __init__(self):
        self.pop = []

    def addPerson(self, pos, ID, suitcase=False):
        p=Personn.Personn(pos, ID, suitcase=False)
        self.pop.append(p)



