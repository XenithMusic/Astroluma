import pyray as ray
from typing import Union
import assets

def draw_text_outline(text:str,posX:int,posY:int,fontSize:int,color:Union[ray.Color,list,tuple]):
    outlineSize = 1
    ray.draw_text(text,posX-outlineSize,posY-outlineSize,fontSize,color)
    ray.draw_text(text,posX-outlineSize,posY+outlineSize,fontSize,color)
    ray.draw_text(text,posX+outlineSize,posY-outlineSize,fontSize,color)
    ray.draw_text(text,posX+outlineSize,posY+outlineSize,fontSize,color)

class RayfontAFAbst(assets.Font):
    def __init__(self,sourceFile=None):
        pass
    def drawChr(self,chr,x,y,color,scale=1):
        self.drawStr(chr,x,y,color,scale)
    def drawStr(self,str,x,y,color,scale=1):
        ray.draw_text(str,x,y,round(scale*20),color)
    def drawStrOutline(self,str,x,y,color,scale=1):
        self.drawStr(str,x-1,y-1,color,scale)
        self.drawStr(str,x-1,y+1,color,scale)
        self.drawStr(str,x+1,y-1,color,scale)
        self.drawStr(str,x+1,y+1,color,scale)
    def measureStr(self,str,scale=1):
        return ray.measure_text(str,round(scale*20))
    def close(self):
        pass