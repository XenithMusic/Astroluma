import os
from nbt import nbt

class World:
	"""An object that holds a world within a level."""
	def __init__(self, path):
		self.path = path
		print(self.path)

class Level:
	"""An object that holds a level."""
	def __init__(self, path):
		self.path = path
		self.worlds = []
		self.load()
	def load(self):
		for i in os.listdir(f"{self.path.rstrip("/")}/worlds"):
			self.worlds.append(World(f"{self.path.rstrip("/")}/worlds/{i}"))
	def save(self):
		raise NotImplementedError("Uh oh, that's not implemented! (Level.save)")
	def __repr__(self):
		return f"<levels.Level object with {len(self.worlds)} worlds @ {self.path}>"