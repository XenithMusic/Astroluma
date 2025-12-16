import pyray as ray

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.renderStack = {}
        self.queued = []
    def declareScene(self,id,cls):
        self.scenes[id] = cls
    def activateScene(self,id,priority):
        print(f" :: Enabling scene {id}.")
        self.renderStack[priority] = (id,self.scenes[id]())
        print(f" :: Successfully enabled scene {id}!")
    def queueSceneChange(self,id,priority):
        self.queued.append([id,priority])
    def render(self,assets,settings):
        ordered = sorted(self.renderStack.items(),key=lambda scene : scene[0])
        ray.begin_drawing()
        for _,content in ordered:
            id = content[0]
            scene = content[1]
            scene.render(assets,settings,self)
        ray.end_drawing()
        if self.queued != []:
            for i in self.queued:
                self.activateScene(*i)
        return