# global libraries

from raylib import *
from cffi import FFI
ffi = FFI()
import ctypes,time

# local libraries

from enums import *
import const,assets,conf,utils,scenes
import localization as locale

# initialize

SetConfigFlags(FLAG_MSAA_4X_HINT)

InitWindow(600,400,const.NAME.encode() + b" - " + const.SPLASH.encode())
SetTargetFPS(60)
InitAudioDevice()
def doInitFrame(step=b"Initializing",sub=b"",subsub=b""):
	BeginDrawing()
	ClearBackground(BLACK)
	DrawText(step,10,10,20,WHITE)
	DrawText(sub,20,30,20,WHITE)
	DrawText(subsub,30,50,20,WHITE)
	EndDrawing()
doInitFrame()
time.sleep(0.1)

# important constants
NULL = ffi.NULL
true = True
false = False

# load assets
doInitFrame(sub=b"Loading assets...")
a = assets.collect_assets("assets")
print(a)

# load configuration
doInitFrame(sub=b"Loading configuration...")
settings = conf.Config()
settings.makeDefaults(
	{
		"volume":{
			"master":0.25,
			"music":1.0
		},
		"language":locale.language
	})

# load localization
doInitFrame(sub=b"Loading assets...",subsub=b"(localization)")
locale.language = settings.config["language"]
locale.loadLanguage(a)

# extra variables
def HandleMusic(music):
	UpdateMusicStream(music)
	SetMusicVolume(music,settings.config["volume"]["master"]*settings.config["volume"]["music"])

sceneman = scenes.SceneManager()
class MainMenu(scenes.Scene):
	def __init__(self,name):
		super().__init__(name)
	def Process(self,man):
		menuMusic = a["astrolume:music.lastingPeace_extended_ambient"]
		HandleMusic(menuMusic)
		if not IsMusicStreamPlaying(menuMusic):
			PlayMusicStream(a["astrolume:music.lastingPeace_extended_ambient"])
	def Render(self,man):
		DrawTextEx(a["astrolume:fonts.Prompt-ExtraLightItalic"],const.NAME.encode(),(20,10),60,10,WHITE) # text,x,y,size,color
		DrawTextEx(a["astrolume:fonts.Prompt-Regular"],const.VERSION.encode(),(20,s_height-30),20,0,GRAY) # text,x,y,size,color
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.singleplayer"].encode(),(20,150),30,0,WHITE)
	def Event(self,man):
		pass
sceneman.addScene("MAIN_MENU",MainMenu)
sceneman.setScene("MAIN_MENU")

while not WindowShouldClose():
	s_width,s_height = (GetScreenWidth(),GetScreenHeight())
	sceneman.PrepShader(s_width,s_height)
	sceneman.Render()
	sceneman.Process()

assets.destroy_assets(a)
CloseWindow()

settings.save()