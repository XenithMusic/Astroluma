import os,jsonc
from typing import Any
import pyray as ray

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
    def close(self):
        pass

class ShaderContent:
    def __init__(self,sourceFile):
        with open(sourceFile,"r") as f:
            self.code = f.read()
    def close(self):
        pass

class Font:
    def __init__(self,sourceFile):
        print(sourceFile)
        pngf = sourceFile
        jsonf = pngf.replace(".png",".jsonc")
        assert os.path.exists(pngf)
        self.png = ray.load_texture(pngf)
        with open(jsonf,"r") as f:
            self.json:dict = jsonc.loads(f.read())
        self.map = self.json["charmap"]
        self.version = self.json["version"]
        self.grid = self.json["gridsize"]
        self.exceptionals = self.json["exceptionals"]
        self.advance = self.json.get("advanceStandard",self.grid[0])
    def drawChr(self,chr,x,y,color,scale=1):
        foundX = 0
        foundY = 0
        for _y,v in enumerate(self.map):
            if chr in v:
                foundY = _y
                foundX = v.index(chr)
                break
        advance = self.advance
        if chr in self.exceptionals:
            advance = self.exceptionals[chr]
        chrx = foundX*self.grid[0]
        chry = foundY*self.grid[1]
        chrw = (advance-1)
        chrh = self.grid[1]
        rect = ray.Rectangle(chrx,chry,chrw,chrh)
        ray.draw_texture_pro(self.png,rect,(x,y,(chrw*scale),(chrh*scale)),(0,0),0,color)
        return advance*scale
    def drawStr(self,str,x,y,color,scale=1):
        for chr in str:
            x += self.drawChr(chr,x,y,color,scale)
    def close(self):
        ray.unload_texture(self.png)

def getLocales(list):
    return {x.split("/")[-1]:Locale(x + ".lang") for x in list}

def getShaders(list):
    return {x.split("/")[-1]:x + ".glsl" for x in list}

def getFonts(list):
    return {x.split("/")[-1].replace(".font.png",""):Font(x) for x in list if x.endswith(".font.png")}

"""
Asset API
"""

def getCategory(category,namespace="astroluma"):
    return [".".join(x.split(".")[:-1]) for x in os.listdir(loadedNamespaces[namespace] + category)]
def getFulls(category,namespace="astroluma"):
    return [x for x in os.listdir(loadedNamespaces[namespace] + category)]
def loadCategory(category,namespace="astroluma",loadFunc=str,getFunc=getCategory) -> list[Any]:
    return loadFunc([f"{loadedNamespaces[namespace]}{category}/{x}" for x in getFunc(category,namespace)])
class Assets:
    def __init__(self):
        self.locale: list[Locale] = loadCategory("locale",loadFunc=getLocales)
        self.shaders: list[ShaderContent] = loadCategory("shaders",loadFunc=getShaders)
        self.fonts: list[Font] = loadCategory("sprites/font",loadFunc=getFonts,getFunc=getFulls)
    def close(self):
        for i in self.locale:
            i.close()
        for i in self.shaders:
            i.close()
        for i in self.fonts:
            i.close()