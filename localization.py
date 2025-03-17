import locale,os
def loadLanguage(a):
	global language,lang
	if not f"astrolume:locale.{language}" in a:
		language = "en_US"
	lang = a[f"astrolume:locale.{language}"].split("\n")
	lang = {x[0]:" ".join(x[1:]) for x in [x.split(" ") for x in lang]}
language = locale.getdefaultlocale()[0]