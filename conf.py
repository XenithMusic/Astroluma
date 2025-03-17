import json

def merge_defaults(defaults, table):
	for key, value in defaults.items():
		if isinstance(value, dict) and isinstance(table.get(key), dict):
			# Recursively merge if both are dicts
			table[key] = merge_defaults(value, table[key])
		elif key not in table:
			# Only set missing keys
			table[key] = value
	return table

class Config:
	"""An object making saving to a configuration unnecessarily simple."""
	def __init__(self,path="data/settings.json"):
		self.path = path
		try:
			with open(self.path,"r") as f:
				self.config = json.load(f)
		except FileNotFoundError as e:
			self.config = {}
	def save(self,path=None):
		with open(path or self.path,"w") as f:
			json.dump(self.config,f,indent=4)
	def reload(self):
		with open(self.path,"r") as f:
			self.config = json.load(f)
	def makeDefaults(self,defaults):
		self.config = merge_defaults(defaults,self.config)