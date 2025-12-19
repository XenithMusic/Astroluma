class Playtime:
    def __init__(self,seconds):
        self._seconds = seconds
        self.minutes = seconds//60
        self.hours = self.minutes//60
        self.minutes = self.minutes%60
        self.seconds = self._seconds%60