# global libraries

try:
	from raylib import *
except ModuleNotFoundError as e:
	raise ImportError("Dependency not installed. Please run 'pip install raylib'.")
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
		"graphics":{

		},
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

def DrawButtonRectangle(x,y,w,h,color,hovercolor,clickcolor,ID,func,text=""):
	r = None
	if CheckCollisionPointRec(GetMousePosition(),[x,y,w,h]):
		color = hovercolor
		if IsMouseButtonDown(0):
			color = clickcolor
		if IsMouseButtonReleased(0):
			func(ID)
		r = MOUSE_CURSOR_POINTING_HAND
	DrawRectangle(x,y,w,h,color)
	if text != "": DrawTextEx(a["astrolume:fonts.Prompt-Light"],text.encode(),(x+5,y),h,0,WHITE)
	return r
def DrawSliderElement(x,y,w,h,min,max,bgcolor,bghovercolor,bgclickcolor,fgcolor,value=0,scalingfunc=lambda x : x,barWidth=4,text="Lorem Ipsum",displayfunc=lambda x : f"{int(x*100)}%",threshold=1):
	mousePos = GetMousePosition()
	cursor = None
	if CheckCollisionPointRec(mousePos,[x,y,w,h]):
		bgcolor = bghovercolor
		cursor = MOUSE_CURSOR_POINTING_HAND
		if IsMouseButtonDown(0):
			color = bgclickcolor
			normProgress = scalingfunc((mousePos.x-x)/w)
			value = normProgress*(max-min)+min
			print(value)
			if value-min < threshold: value = min
			if max-value < threshold: value = max
	handleX = (value-min)/(max-min)*(w-barWidth)+x
	DrawRectangle(x,y,w,h,bgcolor)
	DrawRectangle(int(handleX),y,int(barWidth),h,fgcolor)
	DrawTextEx(a["astrolume:fonts.Prompt-Light"],displayfunc(value).encode(),(x+5,y),h,0,WHITE)
	DrawTextEx(a["astrolume:fonts.Prompt-Light"],text.encode(),(x+w+5,y),h,0,WHITE)
	return cursor,value

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
				man.setScene("SETTINGS")
				man.returnScene = "MAIN_MENU"
			case "credits":
				print(ID)
			case "exit":
				closeWindow = True
			case _:
				raise NotImplementedError("Unimplemented ID in MainMenu.ButtonPress")
class Settings(scenes.Scene):
	def __init__(self,name):
		super().__init__(name)
		self.subs = []
	def Process(self,man):
		menuMusic = a["astrolume:music.lastingPeace_extended_ambient"]
		HandleMusic(menuMusic)
		if not IsMusicStreamPlaying(menuMusic):
			PlayMusicStream(a["astrolume:music.lastingPeace_extended_ambient"])
	def Render(self,man):
		cursor = MOUSE_CURSOR_DEFAULT
		ClearBackground(BLACK)
		DrawTextEx(a["astrolume:fonts.Prompt-ExtraLightItalic"],const.NAME.encode(),(20,10),60,10,WHITE) # text,x,y,size,color
		if self.subs:
			DrawTextEx(a["astrolume:fonts.Prompt-Italic"],(f"{locale.lang['gui.settings.' + self.subs[-1]]} Settings").encode(),(20,70),20,0,WHITE) # text,x,y,size,color
			match self.subs[-1]:
				case "language":
					cursor = DrawButtonRectangle(15,150,205,20,[255,255,255,20],[255,255,255,35],[255,255,255,50],("setLang_en_US",man),self.ButtonPress,text="English (US)") or cursor
					cursor = DrawButtonRectangle(15,171,205,20,[255,255,255,20],[255,255,255,35],[255,255,255,50],("setLang_de_DE",man),self.ButtonPress,text="Deutsch (Deutschland)") or cursor
				case "video":
					pass
				case "audio":
					_cursor,settings.config["volume"]["master"] = DrawSliderElement(15,150,205,20,0,1,[255,255,255,20],[255,255,255,30],[255,255,255,20],[255,255,255,255],text="Master Volume",value=settings.config["volume"]["master"],threshold=0.03)
					cursor = _cursor or cursor
					_cursor,settings.config["volume"]["music"] = DrawSliderElement(15,171,205,20,0,1,[255,255,255,20],[255,255,255,30],[255,255,255,20],[255,255,255,255],text="Music Volume",value=settings.config["volume"]["music"],threshold=0.03)
					cursor = _cursor or cursor
				case _:
					raise NotImplementedError(f"Settings.Render match self.subs[-1] case {self.subs[-1]}")
		else:
			DrawTextEx(a["astrolume:fonts.Prompt-Italic"],b"Settings",(20,70),20,0,WHITE) # text,x,y,size,color
			DrawTextEx(a["astrolume:fonts.Prompt-Regular"],const.VERSION.encode(),(20,s_height-30),20,0,GRAY) # text,x,y,size,color

			cursor = DrawButtonRectangle(15,150,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("videosettings",man),self.ButtonPress) or cursor
			DrawRectangle(13,150,2,30,[255,255,255,255])
			DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.settings.video"].encode(),(20,150),30,0,WHITE)

			cursor = DrawButtonRectangle(15,181,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("audiosettings",man),self.ButtonPress) or cursor
			DrawRectangle(13,181,2,30,[255,255,255,255])
			DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.settings.audio"].encode(),(20,181),30,0,WHITE)

			cursor = DrawButtonRectangle(15,212,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("languagesettings",man),self.ButtonPress) or cursor
			DrawRectangle(13,212,2,30,[255,255,255,255])
			DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.settings.language"].encode(),(20,212),30,0,WHITE)

		cursor = DrawButtonRectangle(15,274,205,30,[255,255,255,5],[255,255,255,20],[255,255,255,50],("back",man),self.ButtonPress) or cursor
		DrawRectangle(13,274,2,30,[255,255,255,255])
		DrawTextEx(a["astrolume:fonts.Prompt-Light"],locale.lang["gui.settings.back"].encode(),(20,274),30,0,WHITE)
		SetMouseCursor(cursor)
	def Input(self,man):
		pass
	def ButtonPress(self,ID):
		global closeWindow
		man = ID[1]
		ID = ID[0]
		print(ID)
		if ID.startswith("setLang_"):
			locale.language = ID.replace("setLang_","")
			settings.config["language"] = locale.language
			locale.loadLanguage(a)
			ID = "ignore"
		match ID:
			case "ignore":
				pass
			case "videosettings":
				self.subs += ["video"]
			case "audiosettings":
				self.subs += ["audio"]
			case "languagesettings":
				self.subs += ["language"]
			case "back":
				if self.subs != []:
					self.subs.pop()
					return
				man.setScene(man.returnScene)
			case _:
				raise NotImplementedError("Unimplemented ID in Settings.ButtonPress")
sceneman.addScene("MAIN_MENU",MainMenu)
sceneman.addScene("SETTINGS",Settings)
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