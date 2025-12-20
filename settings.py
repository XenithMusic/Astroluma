import os,objects,jsonc

if "data" not in os.listdir():
    os.mkdir("data")
if "saves" not in os.listdir("data"):
    os.mkdir("data/saves")

class World:
    def __init__(self,path):
        self.path = path

class Save:
    def __init__(self,path,name):
        self.worlds = [World(path + "worlds/" + x) for x in os.listdir(path + "worlds/")]
        self.name = name.split(".")[0]
        with open(path + "save.json","r") as f:
            self.meta = jsonc.load(f)
        self.completion = len(self.meta["completion"])
        self.maxCompletion = self.meta["maxCompletion"]
        self.pt = objects.Playtime(self.meta["playtime"])

class Saves:
    def __init__(self,path):
        self.path = path
        self.saves = []
        self.files = os.listdir(self.path)
        for file in self.files:
            self.saves += [Save(self.path + file + "/",file)]

class Settings:
    def __init__(self):
        self.dict = {
            "screen_width":0,
            "screen_height":0,
            "locale":"en_US"
        }
    @property
    def saves(self):
        return Saves("data/saves/")