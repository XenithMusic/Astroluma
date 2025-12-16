import os
from typing import Any

loadedNamespaces = {"astroluma":"assets/"}

"""
Asset loaders
"""

class Locale:
    def __init__(self,sourceFile):
        self.keys = {}
        with open(sourceFile,"r") as f:
            self.data = f.read().split("\n")
        for line in self.data:
            if not "=" in line: continue
            split = line.split("//")[0].split("=")
            self.keys[split[0].rstrip()] = "=".join(split[1:])
    def getKey(self,key,*format):
        if key.startswith("'"):
            text = key[1:]
        else:
            text = self.keys[key]
        return text % format

class ShaderContent:
    def __init__(self,sourceFile):
        with open(sourceFile,"r") as f:
            self.code = f.read()

def getLocales(list):
    return {x.split("/")[-1]:Locale(x + ".lang") for x in list}

def getShaders(list):
    return {x.split("/")[-1]:x + ".glsl" for x in list}


"""
Asset API
"""

def getCategory(category,namespace="astroluma"):
    return [".".join(x.split(".")[:-1]) for x in os.listdir(loadedNamespaces[namespace] + category)]
def loadCategory(category,namespace="astroluma",loadFunc=str) -> list[Any]:
    return loadFunc([f"{loadedNamespaces[namespace]}{category}/{x}" for x in getCategory(category,namespace)])
class Assets:
    def __init__(self):
        self.locale: list[Locale] = loadCategory("locale",loadFunc=getLocales)
        self.shaders: list[ShaderContent] = loadCategory("shaders",loadFunc=getShaders)