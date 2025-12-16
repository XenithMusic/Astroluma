import pyray as ray
import scene
import nodes
import settings
import assets
import const
import time
import math

"""
Init : Raylib
"""

ray.set_config_flags(ray.ConfigFlags.FLAG_MSAA_4X_HINT | ray.ConfigFlags.FLAG_WINDOW_RESIZABLE)
ray.init_window(600,400,"Astroluma")
ray.set_target_fps(60)

"""
Init : Instances
"""

mgr = scene.SceneManager()
cfg = settings.Settings()
ass = assets.Assets()

"""
Init : Modding
"""

MOD_BRAND = "Vanilla"
MOD_COUNT = 0
RESOURCE_COUNT = 0

"""
Init : Scenes
"""

gameTime = 0

class Menu(nodes.Scene):
    def __init__(self):
        super().__init__()

        self.font = ass.fonts["default"]

        self.title = nodes.Text(50,50,"'Astroluma",40,ray.WHITE,outlineColor=ray.BLACK)
        
        self.singlePlayer = nodes.Button(50,150,250,180,text="gui.menu.singleplayer",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        self.singlePlayerAccent = nodes.FillRect(50,150,52,180,ray.WHITE)
        self.singlePlayer.children += [self.singlePlayerAccent]
        
        self.multiPlayer = nodes.Button(50,182,250,212,text="gui.menu.multiplayer",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        self.multiPlayerAccent = nodes.FillRect(50,182,52,212,ray.WHITE)
        self.multiPlayer.children += [self.multiPlayerAccent]
        
        self.settings = nodes.Button(50,214,250,244,text="gui.menu.settings",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        self.settingsAccent = nodes.FillRect(50,214,52,244,ray.WHITE)
        self.settings.children += [self.settingsAccent]
        
        self.exit = nodes.Button(50,246,250,276,text="gui.menu.exit",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        self.exitAccent = nodes.FillRect(50,246,52,276,ray.WHITE)
        self.exit.children += [self.exitAccent]

        self.copyright = nodes.Text(self.w-5,self.h-5,text=f"'Astroluma ({const.VERSION})",size=10,hAlign="right",vAlign="bottom",outlineColor=ray.BLACK)

        self.modded = nodes.Text(5,self.h-5-20,text=f"gui.generic.unloaded",size=10,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
        self.modct = nodes.Text(5,self.h-5-10,text=f"gui.generic.unloaded",size=10,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
        self.rpct = nodes.Text(5,self.h-5,text=f"gui.generic.unloaded",size=10,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
    def _render(self,assets,settings,sceneManager):
        super()._render(assets,settings,sceneManager)
        self.copyright.x = self.w-5
        self.copyright.y = self.h-5
        self.modded.y = self.h-5-30
        self.modct.y = self.h-5-15
        self.rpct.y = self.h-5
        MOD_BRAND = "Vanilla" if MOD_COUNT == 0 else "Modded"
        self.modded.text = f"'{MOD_BRAND}"
        self.modct.text = f"'{MOD_COUNT} mods"
        self.rpct.text = f"'{RESOURCE_COUNT} resource packs"
        self.children = [self.title,self.singlePlayer,self.multiPlayer,self.settings,self.exit,self.copyright,self.modded,self.modct,self.rpct]
        self.font.drawStr("Hello, World!",15,15,(0,0,0,255),scale=3)

class Sky(nodes.Scene):
    def __init__(self):
        super().__init__()
        self.fill = nodes.FillRect(0,0,1000,1000,ray.WHITE,[])
        self.children += [self.fill]
        print(ass.shaders["sky_frag"])
        self.shader = ray.load_shader(ass.shaders["base_vert"],ass.shaders["sky_frag"])
        self.time_loc = ray.get_shader_location(self.shader,"time")
        self.resolution_loc = ray.get_shader_location(self.shader,"resolution")
        if not ray.is_shader_valid(self.shader):
            print(" << !! >> Shader invalid!")
            exit()
        print("AAA")
    def _render(self,assets,settings,sceneManager):
        gameTime = ray.get_time()/30
        super()._render(assets,settings,sceneManager)
        self.fill.w = self.w
        self.fill.h = self.h
        ray.begin_shader_mode(self.shader)
        ray.set_shader_value(self.shader,self.time_loc,ray.ffi.new("float *",gameTime),ray.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        print(self.w/1,self.h/1)
        ray.set_shader_value(self.shader,self.resolution_loc,ray.ffi.new('float[]',[self.w/1,self.h/1]),ray.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
    def _endRender(self, assets, settings, sceneManager):
        ray.end_shader_mode()

mgr.declareScene("menu",Menu)
mgr.declareScene("sky",Sky)
mgr.activateScene("menu",0)
mgr.activateScene("sky",-9999)

"""
Main
"""

while not ray.window_should_close():
    mgr.render(ass,cfg)

"""
Shutdown : Garbage
"""

ray.close_window()