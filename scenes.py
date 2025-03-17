from raylib import *
import pyray
import utils

def DrawTextureFlip(texture,x,y,color):
	DrawTextureRec(texture, \
		(pyray.Rectangle(0, 0, texture.width, -texture.height)), \
		(pyray.Vector2(x, y)), 
		WHITE)

class SceneError(Exception):
	"""An error for generic failures in the scenes module."""
	def __init__(self, arg):
		super().__init__(arg)

class Scene:
	"""A scene, which dummy implements a Process, Render, and Event function"""
	def __init__(self,name):
		self.name = name
	def Process(self,man):
		raise NotImplementedError(f"({self.name}) Scene.Process")
	def Render(self,man):
		raise NotImplementedError(f"({self.name}) Scene.Render")
	def Input(self,man):
		raise NotImplementedError(f"({self.name}) Scene.Event")

class SceneManager:
	"""docstring for SceneManager"""
	def __init__(self):
		self.scenes = {}
		self.active_scene = None
		self.screen_width = 0
		self.screen_height = 0
		self.renderTextures = []
		self.shaders = {}
	def PrepShader(self,width,height):
		if GetScreenWidth() != self.screen_width or GetScreenHeight() != self.screen_height or len(self.renderTextures) == 0:
			self.screen_width = GetScreenWidth()
			self.screen_height = GetScreenHeight()
			texelSize = ffi.new("float[2]", [1.0/self.screen_width, 1.0/self.screen_height])
			resolution = ffi.new("float[2]", [self.screen_width, self.screen_height])
			for i in self.shaders.values():
				SetShaderValue(i, GetShaderLocation(i, b"resolution"), resolution, SHADER_UNIFORM_VEC2)
				SetShaderValue(i, GetShaderLocation(i, b"texelSize"), texelSize, SHADER_UNIFORM_VEC2)
			for i in self.renderTextures:
				UnloadRenderTexture(i)
			self.renderTextures = [
				LoadRenderTexture(self.screen_width,self.screen_height),
				LoadRenderTexture(self.screen_width,self.screen_height),
				LoadRenderTexture(self.screen_width,self.screen_height),
				LoadRenderTexture(self.screen_width,self.screen_height)
			]
			print(self.renderTextures)
			print(self.screen_width)
			print(self.screen_height)
	def addScene(self,name,scene):
		if not issubclass(scene,Scene):
			raise TypeError("Expected a Scene.")
		self.scenes[name] = scene
	def addShader(self,name,shader):
		self.shaders[name] = shader
	def setScene(self,scene):
		self.active_scene = self.scenes[scene](scene)
	def getScene(self):
		return self.active_scene.name
	def Process(self):
		if not self.active_scene: raise SceneError("No active scene!")
		return self.active_scene.Process(self)
	def Render(self):
		if not self.active_scene: raise SceneError("No active scene!")
		renderTextureId = 0
		BeginTextureMode(self.renderTextures[renderTextureId])
		self.active_scene.Render(self)
		EndTextureMode()
		for k,v in self.shaders.items():
			renderTextureId = utils.wrap(renderTextureId+1,0,3)
			BeginTextureMode(self.renderTextures[renderTextureId])
			BeginShaderMode(v)

			DrawTextureFlip(self.renderTextures[utils.wrap(renderTextureId-1,0,3)].texture,0,0,WHITE)

			EndShaderMode()
			EndTextureMode()
		BeginDrawing()
		ClearBackground(BLACK)
		DrawTextureFlip(self.renderTextures[renderTextureId].texture,0,0,WHITE)
		EndDrawing()
	def Input(self):
		if not self.active_scene: raise SceneError("No active scene!")
		return self.active_scene.Input(self)