import pyray as ray
from typing import Union

def draw_text_outline(text:str,posX:int,posY:int,fontSize:int,color:Union[ray.Color,list,tuple]):
    outlineSize = 1
    ray.draw_text(text,posX-outlineSize,posY-outlineSize,fontSize,color)
    ray.draw_text(text,posX-outlineSize,posY+outlineSize,fontSize,color)
    ray.draw_text(text,posX+outlineSize,posY-outlineSize,fontSize,color)
    ray.draw_text(text,posX+outlineSize,posY+outlineSize,fontSize,color)