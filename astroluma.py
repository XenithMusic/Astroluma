import pyray as ray
import debug as d
import scene
import nodes
import settings
import assets
import const
import time
import math
import mods

"""
Init : Raylib
"""

d.debug("Init : Raylib")
ray.set_config_flags(ray.ConfigFlags.FLAG_MSAA_4X_HINT | ray.ConfigFlags.FLAG_WINDOW_RESIZABLE)
ray.init_window(600,400,"Astroluma")
ray.set_target_fps(60)

"""
Init : Instances
"""

d.debug("Init : Instances")
cfg = settings.Settings()
ass = assets.Assets()
mgr = scene.SceneManager(ass,cfg)

"""
Init : Defaults
"""

d.debug("Init : Defaults")
nodes.defaultFont = ass.fonts["default"]

"""
Init : Modding
"""

d.debug("Init : Modding")

mods.init(ass,cfg)
mods = mods.discover_mods()

for i in mods:
    print(i.run_script("init",["init"]))

MOD_BRAND = "Vanilla"
MOD_COUNT = len(mods)
RESOURCE_COUNT = 0

"""
Init : Scenes
"""

d.debug("Init : Scenes")
gameTime = 0

class Menu(nodes.Scene):
    def __init__(self):
        super().__init__()

        self.font = ass.fonts["default"]

        self.title = nodes.Text(50,50,"'Astroluma",64,ray.WHITE,outlineColor=ray.BLACK)

        self.copyright = nodes.Text(self.w-5,self.h-5,text=f"'Astroluma ({const.CURRENT_VERSION['GAME']})",size=16,hAlign="right",vAlign="bottom",outlineColor=ray.BLACK)

        self.modded = nodes.Text(5,self.h-5-32,text=f"gui.generic.unloaded",size=16,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
        self.modct = nodes.Text(5,self.h-5-16,text=f"gui.generic.unloaded",size=16,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
        self.rpct = nodes.Text(5,self.h-5,text=f"gui.generic.unloaded",size=16,hAlign="left",vAlign="bottom",outlineColor=ray.BLACK)
    def _render(self,assets,settings,sceneManager,parent):
        global close
        super()._render(assets,settings,sceneManager,parent)
        self.copyright.x = self.w-5
        self.copyright.y = self.h-5
        self.modded.y = self.h-5-30
        self.modct.y = self.h-5-15
        self.rpct.y = self.h-5
        MOD_BRAND = "Vanilla" if MOD_COUNT == 0 else "Modded"
        self.modded.text = f"'{MOD_BRAND}"
        self.modct.text = f"'{MOD_COUNT} mods"
        self.rpct.text = f"'{RESOURCE_COUNT} resource packs"
        self.children = [self.title,self.copyright,self.modded,self.modct,self.rpct]

class Menu_Base(nodes.Scene):
    def __init__(self):
        super().__init__()

        self.font = ass.fonts["default"]
        
        self.singlePlayer = nodes.Button(50,150,250,180,text="gui.menu.singleplayer",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        # self.singlePlayerAccent = nodes.FillRect(0,0,3,30,ray.WHITE)
        # self.singlePlayer.children += [self.singlePlayerAccent]
        
        self.multiPlayer = nodes.Button(50,182,250,212,text="gui.menu.multiplayer",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        # self.multiPlayerAccent = nodes.FillRect(0,0,3,30,ray.WHITE)
        # self.multiPlayer.children += [self.multiPlayerAccent]
        
        self.settings = nodes.Button(50,214,250,244,text="gui.menu.settings",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        # self.settingsAccent = nodes.FillRect(0,0,3,30,ray.WHITE)
        # self.settings.children += [self.settingsAccent]
        
        self.exit = nodes.Button(50,246,250,276,text="gui.menu.exit",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)
        # self.exitAccent = nodes.FillRect(0,0,3,30,ray.WHITE)
        # self.exit.children += [self.exitAccent]
    def _render(self,assets,settings,sceneManager,parent):
        global close
        super()._render(assets,settings,sceneManager,parent)
        self.children = [self.singlePlayer,self.multiPlayer,self.settings,self.exit]
        if self.exit.clicked():
            sceneManager.shutdown()
        if self.singlePlayer.clicked():
            sceneManager.activateScene("menu:saves",1)

class Menu_Saves(nodes.Scene):
    def __init__(self):
        super().__init__()
        self.font = ass.fonts["default"]
        self.texts = []
        
        for i,v in enumerate(cfg.saves.saves):
            self.texts += [nodes.Button(50,150+(i*35),450,180+(i*35),text=f"'",hAlign="center",textOffset=(0,0),buttonColor=ray.Color(255,255,255,50),fontColor=ray.WHITE,outlineColor=ray.BLACK,borderColor=None)]
            subtext = nodes.Text(200,30,f"gui.menu.saves.sub%%{round(v.completion/v.maxCompletion*100)}%%{time.strftime("%H : %M",time.gmtime(v.pt._seconds))}",hAlign="center",vAlign="bottom",outlineColor=ray.BLACK)
            supertext = nodes.Text(200,0,f"'{v.name}",hAlign="center",vAlign="top",outlineColor=ray.BLACK)
            self.texts[-1].children += [subtext,supertext]
        # self.singlePlayerAccent = nodes.FillRect(0,0,3,30,ray.WHITE)
        # self.singlePlayer.children += [self.singlePlayerAccent]
        
    def _render(self,assets,settings,sceneManager,parent):
        self.children = self.texts

class Sky(nodes.Scene):
    def __init__(self):
        super().__init__()
        self.fill = nodes.FillRect(0,0,1000,1000,ray.WHITE,[])
        self.children += [self.fill]
        self.shader = ray.load_shader(ass.shaders["base_vert"],ass.shaders["sky_frag"])
        self.time_loc = ray.get_shader_location(self.shader,"time")
        self.resolution_loc = ray.get_shader_location(self.shader,"resolution")
        if not ray.is_shader_valid(self.shader):
            d.fatal("Sky shader failed to load. Please check the logs immediately before this message for a 'Compile error'.",exitCode=70)
    def _render(self,assets,settings,sceneManager,parent):
        gameTime = ray.get_time()/30
        super()._render(assets,settings,sceneManager,parent)
        self.fill.w = self.w
        self.fill.h = self.h
        ray.begin_shader_mode(self.shader)
        ray.set_shader_value(self.shader,self.time_loc,ray.ffi.new("float *",gameTime),ray.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        ray.set_shader_value(self.shader,self.resolution_loc,ray.ffi.new('float[]',[self.w/1,self.h/1]),ray.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
    def _endRender(self, assets, settings, sceneManager, parent):
        ray.end_shader_mode()

mgr.declareScene("menu",Menu)
mgr.declareScene("menu:base",Menu_Base)
mgr.declareScene("menu:saves",Menu_Saves)
mgr.declareScene("sky",Sky)
mgr.activateScene("menu",0)
mgr.activateScene("menu:base",1)
mgr.activateScene("sky",-9999)

def _shutdown(assets,settings,sceneManager):
    d.info("Shutting down!")

mgr.setCallback("shutdown",_shutdown)

"""
Main
"""

d.debug("Main")
close = False
while not mgr.should_close:
    mgr.render()
    if ray.window_should_close():
        mgr.shutdown()

"""
Shutdown : Garbage
"""

d.debug("Shutdown : Garbage")
ray.close_window()

"""
Shutdown : Terminate
"""

d.debug("Shutdown : Terminate")
exit(mgr.close_exit_code)