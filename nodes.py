import pyray as ray
from scene import *

import pyrayExtensions as rayx

class Node:
    def __init__(self,x,y,children=[]):
        self.x = x
        self.y = y
        self.children = children
    def render(self,assets,settings,sceneManager:SceneManager):
        self._render(assets,settings,sceneManager)
        for i in self.children:
            i.render(assets,settings,sceneManager)
        self._endRender(assets,settings,sceneManager)
    def _render(self,assets,settings,sceneManager:SceneManager):
        raise NotImplementedError(f"Node._render not implemented in {self.__class__}.")
    def _endRender(self,assets,settings,sceneManager:SceneManager):
        pass

class CollectionNode(Node):
    def __init__(self,x,y,children=[]):
        super().__init__(x,y,children)
    def _render(self,assets,settings,sceneManager:SceneManager):
        pass

class SuperNode(CollectionNode):
    def __init__(self,children=[]):
        super().__init__(-1,-1,children)

class FillRect(Node):
    def __init__(self,x,y,x2,y2,color=ray.BLACK,children=[]):
        super().__init__(x,y,children)
        self.w = x2-x
        self.h = y2-y
        self.color = color
    def _render(self,assets,settings,sceneManager:SceneManager):
        if self.color == None: return
        ray.draw_rectangle(self.x,self.y,self.w,self.h,self.color)

class BorderRect(Node):
    def __init__(self,x,y,x2,y2,color=ray.BLACK,children=[]):
        super().__init__(x,y,children)
        self.w = x2-x
        self.h = y2-y
        self.color = color
    def _render(self,assets,settings,sceneManager:SceneManager):
        if self.color == None: return
        ray.draw_rectangle_lines(self.x,self.y,self.w,self.h,self.color)

class Scene(SuperNode):
    def __init__(self):
        super().__init__([])
        self.w = 0
        self.h = 0
    def _render(self,assets,settings,sceneManager:SceneManager):
        self.w = ray.get_screen_width()
        self.h = ray.get_screen_height()
        settings.screen_width = self.w
        settings.screen_height = self.h

defaultFont = rayx.RayfontAFAbst()

class Text(Node):
    def __init__(self,x,y,text="meta.text.defaultText",size=16,color=ray.RAYWHITE,hAlign="left",vAlign="top",outlineColor=None,font=None):
        global defaultFont
        if font == None: font = defaultFont
        super().__init__(x,y)
        self.text = text
        self.fontSize = size
        self.fontColor = color
        self.initialized = False
        self.hAlignSet = hAlign
        self.vAlignSet = vAlign
        self.outlineColor = outlineColor
        self.font = font
    def _render(self,assets,settings,sceneManager:SceneManager):
        if self.initialized == False: self.postRenderInit(assets,settings,sceneManager)
        if self.outlineColor:
            self.font.drawStrOutline(assets.locale[settings.locale].getKey(self.text),self.x-self.hAlign,self.y-self.vAlign,self.outlineColor,self.fontSize/16)
        self.font.drawStr(assets.locale[settings.locale].getKey(self.text),self.x-self.hAlign,self.y-self.vAlign,self.fontColor,self.fontSize/16)
    def postRenderInit(self,assets,settings,sceneManager:SceneManager):
        self.w = self.font.measureStr(assets.locale[settings.locale].getKey(self.text),self.fontSize/16)
        self.h = self.fontSize
        self.hAlign = 0
        self.vAlign = 0
        if self.hAlignSet == "center":
            self.hAlign = self.w//2
        if self.hAlignSet == "right":
            self.hAlign = self.w
        if self.vAlignSet == "center":
            self.vAlign = self.h//2
        if self.vAlignSet == "bottom":
            self.vAlign = self.h
        print(self.hAlign,self.vAlign)
        self.initialized = True

class Button(CollectionNode):
    def __init__(self,x,y,x2,y2,visualElement=Text,text="meta.defaultText",fontSize=16,buttonColor=ray.RAYWHITE,fontColor=ray.BLACK,
                 hAlign="center",vAlign="center",textOffset=(0,0),borderColor=ray.RAYWHITE,outlineColor=None):
        self.w = x2-x
        self.h = y2-y
        self.text = text
        self.fontSize = fontSize
        self.buttonColor = buttonColor
        self.fontColor = fontColor
        self.borderColor = borderColor
        self.outlineColor = outlineColor

        self.hAlignment = textOffset[0]
        self.vAlignment = textOffset[1]
        if hAlign == "center":
            self.hAlignment += self.w//2
        if hAlign == "right":
            self.hAlignment += self.w
        if vAlign == "center":
            self.vAlignment += self.h//2
        if vAlign == "bottom":
            self.vAlignment += self.h

        children = [
            FillRect(x,y,x+self.w,y+self.h,self.buttonColor,
                [
                    BorderRect(x,y,x+self.w,y+self.h,self.borderColor),
                    visualElement(x+self.hAlignment,y+self.vAlignment,self.text,self.fontSize,self.fontColor,hAlign=hAlign,vAlign=vAlign,outlineColor=self.outlineColor)
                ])
        ]
        super().__init__(x,y,children)
    def hovered(self):
        return ray.check_collision_point_rec(ray.get_mouse_position(),(self.x,self.y,self.w,self.h))
    def clicked(self):
        return self.hovered() and ray.is_mouse_button_released(ray.MouseButton.MOUSE_BUTTON_LEFT)