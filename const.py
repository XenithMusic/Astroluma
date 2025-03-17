import random
NAME = "ASTRO·LUMA"
VERSION = "0.1.0-dev"
with open("assets/splash.txt","r") as f: SPLASHTEXTS = [x for x in f.read().split("\n") if x != ""]
SPLASH = SPLASHTEXTS[random.randint(0,len(SPLASHTEXTS)-1)]