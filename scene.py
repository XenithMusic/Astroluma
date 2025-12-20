import pyray as ray
import debug as d
import registrations

class SceneManager:
    def __init__(self,assets,settings):
        self.scenes = {}
        self.renderStack = {}
        self.queued = []
        self.should_close = False
        self.close_exit_code = 0
        self.callbacks = {"shutdown":lambda a,b,c : d.warn("Default shutdown callback found while shutting down. No garbage collection is occurring!")}
        self.assets = assets
        self.settings = settings
        self.shared = {}
    def declareScene(self,id,cls):
        if id in registrations.menuOverrides:
            cls = registrations.menuOverrides[id]
            cls = registrations.menus[cls][1]
        self.scenes[id] = cls
    def activateScene(self,id,priority):
        d.debug(f"Enabling scene {id} with priority {priority}.")
        self.renderStack[priority] = (id,self.scenes[id]())
        d.debug(f"Successfully enabled scene {id}!")
    def queueSceneChange(self,id,priority):
        self.queued.append([id,priority])
    def render(self):
        ordered = sorted(self.renderStack.items(),key=lambda scene : scene[0])
        ray.begin_drawing()
        for _,content in ordered:
            id = content[0]
            scene = content[1]
            scene.render(self.assets,self.settings,self)
        ray.end_drawing()
        if self.queued != []:
            for i in self.queued:
                self.activateScene(*i)
        return
    def shutdown(self,exitCode=0):
        self.should_close = True
        self.invokeCallback("shutdown")
        self.close_exit_code = exitCode
    def setCallback(self,name,function):
        self.callbacks[name] = function
    def invokeCallback(self,name):
        self.callbacks[name](self.assets,self.settings,self)