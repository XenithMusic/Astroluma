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

def DrawButtonRectangle(x,y,w,h,color,hovercolor,clickcolor,ID,func):
	r = None
	if CheckCollisionPointRec(GetMousePosition(),[x,y,w,h]):
		color = hovercolor
		if IsMouseButtonDown(0):
			color = clickcolor
		if IsMouseButtonReleased(0):
			func(ID)
		r = MOUSE_CURSOR_POINTING_HAND
	DrawRectangle(x,y,w,h,color)
	return r

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
		cursor = MOUSE_CURSOR_DEFAULT
		ClearBackground(BLACK)
		DrawTextEx(a["astrolume:fonts.Prompt-ExtraLightItalic"],const.NAME.encode(),(20,10),60,10,WHITE) # text,x,y,size,color
		DrawTextEx(a["astrolume:fonts.Prompt-Regular"],const.VERSION.encode(),(20,s_height-30),20,0,GRAY) # text,x,y,size,color

		cursor = DrawButtonRectangle(15,150,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("singleplayer",man),self.ButtonPress) or cursor
		DrawRectangle(13,150,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.singleplayer"].encode(),(20,150),30,0,WHITE)

		cursor = DrawButtonRectangle(15,181,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("multiplayer",man),self.ButtonPress) or cursor
		DrawRectangle(13,181,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.multiplayer"].encode(),(20,181),30,0,WHITE)

		cursor = DrawButtonRectangle(15,212,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("settings",man),self.ButtonPress) or cursor
		DrawRectangle(13,212,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.settings"].encode(),(20,212),30,0,WHITE)

		cursor = DrawButtonRectangle(15,243,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("credits",man),self.ButtonPress) or cursor
		DrawRectangle(13,243,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.credits"].encode(),(20,243),30,0,WHITE)

		cursor = DrawButtonRectangle(15,274,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("exit",man),self.ButtonPress) or cursor
		DrawRectangle(13,274,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.menu.exit"].encode(),(20,274),30,0,WHITE)
		SetMouseCursor(cursor)
	def Input(self,man):
		pass
	def ButtonPress(self,ID):
		global closeWindow
		man = ID[1]
		ID = ID[0]
		match ID:
			case "singleplayer":
				print("singleplayer")
			case "multiplayer":
				print(ID)
			case "settings":
				print(ID)
			case "credits":
				print(ID)
			case "exit":
				closeWindow = True
			case _:
				raise NotImplementedError("Unimplemented ID in MainMenu.ButtonPress")
sceneman.addScene("MAIN_MENU",MainMenu)
sceneman.setScene("MAIN_MENU")

closeWindow = False

while not (WindowShouldClose() or closeWindow):
	s_width,s_height = (GetScreenWidth(),GetScreenHeight())
	sceneman.PrepShader(s_width,s_height)
	sceneman.Render()
	sceneman.Process()

assets.destroy_assets(a)
CloseWindow()

settings.save()