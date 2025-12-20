import pyray as ray
from scene import *

import pyrayExtensions as rayx

class Node:
    def __init__(self,x,y,children=[]):
        self.x = x
        self.y = y
        self.children = children
    def render(self,assets,settings,sceneManager:SceneManager,parent=(0,0)):
        self.parent = parent
        self._startRender(assets,settings,sceneManager,parent)
        self._render(assets,settings,sceneManager,parent)
        for i in self.children:
            i.parent = (parent[0]+self.x,parent[1]+self.y)
            i.render(assets,settings,sceneManager,(parent[0]+self.x,parent[1]+self.y))
        self._endRender(assets,settings,sceneManager,parent)
    def _startRender(self,assets,settings,sceneManager:SceneManager,parent):
        pass
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        raise NotImplementedError(f"Node._render not implemented in {self.__class__}.")
    def _endRender(self,assets,settings,sceneManager:SceneManager,parent):
        pass

class CollectionNode(Node):
    def __init__(self,x,y,children=[]):
        super().__init__(x,y,children)
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
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
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        if self.color == None: return
        ray.draw_rectangle(self.x+parent[0],self.y+parent[1],self.w,self.h,self.color)

class BorderRect(Node):
    def __init__(self,x,y,x2,y2,color=ray.BLACK,children=[]):
        super().__init__(x,y,children)
        self.w = x2-x
        self.h = y2-y
        self.color = color
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        if self.color == None: return
        ray.draw_rectangle_lines(self.x+parent[0],self.y+parent[1],self.w,self.h,self.color)

class Scene(SuperNode):
    def __init__(self):
        super().__init__([])
        self.w = 0
        self.h = 0
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        self.w = ray.get_screen_width()
        self.h = ray.get_screen_height()
        settings.dict["screen_width"] = self.w
        settings.dict["screen_height"] = self.h

class LuaScene(Scene):
    def __init__(self):
        super().__init__()
        self.shared = {}
        self.luafn["init"](self.shared)
    def __prerender(self,px,py): # for lua
        raise NotImplementedError("__prerender")
    def __render(self,px,py): # for lua
        raise NotImplementedError("__render")
    def __postrender(self,px,py): # for lua
        raise NotImplementedError("__postrender")
    def _startRender(self, assets, settings, sceneManager,parent):
        self.luafn["prerender"](self.shared,parent[0],parent[1])
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        self.shared["w"] = ray.get_screen_width()
        self.shared["h"] = ray.get_screen_height()
        settings.dict["screen_width"] = self.w
        settings.dict["screen_height"] = self.h
        self.luafn["render"](self.shared,parent[0],parent[1])
    def _endRender(self, assets, settings, sceneManager,parent):
        self.luafn["postrender"](self.shared,parent[0],parent[1])
        self.children = self.luafn["children"](self.shared,parent[0],parent[1])

class Holder(CollectionNode):
    def __init__(self,children,x,y,w,h):
        self.items = children
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        super().__init__([])
    def _render(self, assets, settings, sceneManager,parent):
        self.item.x = self.x-(self.w//2)+parent[0]
        self.item.y = self.y-(self.h//2)+parent[1]

defaultFont = rayx.RayfontAFAbst()

class Text(Node):
    def __init__(self,x,y,text="meta.text.defaultText",size=16,color=ray.RAYWHITE,hAlign="left",vAlign="top",outlineColor=None,font=None):
        global defaultFont
        if font == None: font = defaultFont
        super().__init__(x,y)
        self.text = text.split("%%")[0]
        self.text_replacements = text.split("%%")[1:]
        self.fontSize = size
        self.fontColor = color
        self.initialized = False
        self.hAlignSet = hAlign
        self.vAlignSet = vAlign
        self.outlineColor = outlineColor
        self.font = font
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        if self.initialized == False: self.postRenderInit(assets,settings,sceneManager)
        if self.outlineColor:
            self.font.drawStrOutline(assets.locale[settings.dict["locale"]].getKey(self.text,*self.text_replacements),self.x-self.hAlign+parent[0],self.y-self.vAlign+parent[1],self.outlineColor,self.fontSize/16)
        self.font.drawStr(assets.locale[settings.dict["locale"]].getKey(self.text,*self.text_replacements),self.x-self.hAlign+parent[0],self.y-self.vAlign+parent[1],self.fontColor,self.fontSize/16)
    def postRenderInit(self,assets,settings,sceneManager:SceneManager):
        # print(self.text_replacements)
        self.w = self.font.measureStr(assets.locale[settings.dict["locale"]].getKey(self.text,*self.text_replacements),self.fontSize/16)
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
        # print(self.hAlign,self.vAlign)
        self.initialized = True

class Button(CollectionNode):
    def __init__(self,x,y,x2,y2,visualElement=Text,text="meta.defaultText",fontSize=16,buttonColor=ray.RAYWHITE,fontColor=ray.BLACK,
                 hAlign="center",vAlign="center",textOffset=(0,0),borderColor=ray.RAYWHITE,outlineColor=None,accentColor=ray.WHITE):
        self.w = x2-x
        self.h = y2-y
        self.text = text
        self.fontSize = fontSize
        self.buttonColor = buttonColor
        self.fontColor = fontColor
        self.borderColor = borderColor
        self.outlineColor = outlineColor
        self.accentColor = accentColor

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
            FillRect(0,0,self.w,self.h,self.buttonColor,
                [
                    FillRect(0,0,self.w,self.h,self.borderColor),
                    FillRect(0,0,3,30,self.accentColor),
                    visualElement(self.hAlignment,self.vAlignment,self.text,self.fontSize,self.fontColor,hAlign=hAlign,vAlign=vAlign,outlineColor=self.outlineColor)
                ])
        ]
        self.initialized = False
        super().__init__(x,y,children)
    def _render(self,assets,settings,sceneManager:SceneManager,parent):
        self.parent = parent
        self.initialized = True
    def hovered(self):
        return self.initialized and ray.check_collision_point_rec(ray.get_mouse_position(),(self.x+self.parent[0],self.y+self.parent[1],self.w,self.h))
    def clicked(self):
        return self.hovered() and ray.is_mouse_button_released(ray.MouseButton.MOUSE_BUTTON_LEFT)