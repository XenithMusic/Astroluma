import os,jsonc,const
import debug as d
from typing import Any
import pyray as ray
import PIL.Image

loadedNamespaces = {"astroluma":"assets/"}

"""
Asset loaders
"""

class Locale:
    def __init__(self,sourceFile):
        self.keys = {}
        self.name = sourceFile.split("/")[-1]
        with open(sourceFile,"r") as f:
            self.data = f.read().split("\n")
        for line in self.data:
            if not "=" in line: continue
            split = line.split("//")[0].split("=")
            self.keys[split[0].rstrip()] = "=".join(split[1:]).lstrip()
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
        self.headerPixels = 1 # how many pixels that are not counted in the "gridsize", which is only for rendered size.
        d.debug(sourceFile,debugLevel=2)
        pngf = sourceFile
        jsonf = pngf.replace(".png",".jsonc")
        assert os.path.exists(pngf)
        self.png = ray.load_texture(pngf)
        with open(jsonf,"r") as f:
            self.json:dict = jsonc.loads(f.read())
        self.version = self.json["version"]

        if self.version != const.CURRENT_VERSION["FONT"]:
            raise RuntimeError("Out of date font.")

        self.map = self.json["charmap"]
        self.grid = self.json["gridsize"]
        self.advancestd = self.json.get("advanceStandard",self.grid[0])
        self.advances = {}
        self.pilpng = PIL.Image.open(pngf,"r")
        if self.pilpng.mode != "RGBA":
            self.pilpng = self.pilpng.convert("RGBA")
        for y,line in enumerate(self.map):
            for x,chr in enumerate(line):
                topleft = (x*self.grid[0],y*(self.grid[1]+self.headerPixels))
                for i in range(self.grid[0]):
                    self.advances[chr] = self.advancestd
                    if self.pilpng.getpixel((topleft[0]+i,topleft[1]))[3] != 0:
                        self.advances[chr] = i+2
                        break
    def drawChr(self,chr,x,y,color,scale=1):
        foundX = 0
        foundY = 0
        for _y,v in enumerate(self.map):
            if chr in v:
                foundY = _y
                foundX = v.index(chr)
                break
        advance = self.advances[chr]
        chrx = foundX*self.grid[0]
        chry = foundY*(self.grid[1]+self.headerPixels)+1
        chrw = (advance-1)
        chrh = self.grid[1]
        rect = ray.Rectangle(chrx,chry,chrw,chrh)
        ray.draw_texture_pro(self.png,rect,(x,y,(chrw*scale),(chrh*scale)),(0,0),0,color)
        return advance*scale
    def drawStr(self,str,x,y,color,scale=1):
        for chr in str:
            x += self.drawChr(chr,x,y,color,scale)
    def drawStrOutline(self,str,x,y,color,scale=1):
        self.drawStr(str,x-1,y-1,color,scale)
        self.drawStr(str,x-1,y+1,color,scale)
        self.drawStr(str,x+1,y-1,color,scale)
        self.drawStr(str,x+1,y+1,color,scale)
    def measureStr(self,str,scale=1):
        len = 0
        for chr in str:
            len += self.advances[chr]
        return len*scale
    def close(self):
        ray.unload_texture(self.png)

def getLocales(list):
    return {x.split("/")[-1]:Locale(x + ".lang") for x in list}

def getShaders(list):
    return {x.split("/")[-1]:x + ".glsl" for x in list}

def getFonts(list):
    return {x.split("/")[-1].replace(".font.png",""):Font(x) for x in list if x.endswith(".font.png")}

def getScripts(list):
    ret = {}
    for x in list:
        with open(x + ".lua","r") as f:
            ret[x.split("/")[-1].replace(".lua","")] = f.read()
    return ret

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
    def __init__(self,displaying=True):
        self.scripts: list[str] = loadCategory("scripts",loadFunc=getScripts)

        self.locale: list[Locale] = loadCategory("locale",loadFunc=getLocales)
        for i in self.locale["en_US"].keys:
            for name,lang in self.locale.items():
                if not i in lang.keys:
                    d.warn(f"Missing key in language {name}: {i}")
        
        self.shaders: list[ShaderContent] = loadCategory("shaders",loadFunc=getShaders)

        if displaying == True: self.fonts: list[Font] = loadCategory("sprites/font",loadFunc=getFonts,getFunc=getFulls)
    def close(self):
        for i in self.locale:
            i.close()
        for i in self.shaders:
            i.close()
        for i in self.fonts:
            i.close()