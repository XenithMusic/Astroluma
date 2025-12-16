import pyray as ray

class SceneManager:
    def __init__(self,assets,settings):
        self.scenes = {}
        self.renderStack = {}
        self.queued = []
        self.should_close = False
        self.close_exit_code = 0
        self.callbacks = {"shutdown":lambda a,b,c : 0}
        self.assets = assets
        self.settings = settings
    def declareScene(self,id,cls):
        self.scenes[id] = cls
    def activateScene(self,id,priority):
        print(f" :: Enabling scene {id}.")
        self.renderStack[priority] = (id,self.scenes[id]())
        print(f" :: Successfully enabled scene {id}!")
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