class Personn():
    def __init__(self, pos, ID, suitcase=False):
        self.pos = pos
        self.ID = ID
        self.img = None
        self.suitcase = []
        self.NbSuitcase = len(self.suitcase)
        self.suitcaseImg = None

    def __str__(self):
        return f"ID: {self.ID}, pos: {self.pos}, suitcase: {self.suitcase}"


