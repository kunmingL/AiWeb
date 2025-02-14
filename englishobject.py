class enlishObject:
    def __init__(self, Esentence, Csentence,words):
        self.Esentence = Esentence
        self.Csentence = Csentence
        self.words = words

    def __repr__(self):
        return f"Object(Esentence={self.Esentence}, Csentence={self.Csentence}, words={self.words})"