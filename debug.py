import colors,const,time,os

if "logs" not in os.listdir():
    os.mkdir("logs")

name = f"logs/{time.strftime('date_%M_%d_%Y time_%H;%M;%S.log')}"
with open(name,"w"):
    pass
f = open(name,"a",buffering=1)

def createMessage(msg):
    print(msg)
    f.write(msg + "\n")

def debug(msg,debugLevel=1):
    if const.DEBUG < debugLevel: return False
    createMessage(f"{colors.GRAY}{colors.ITALIC} -- {' '*(debugLevel*4)} {msg}{colors.RESET}")
    return True

def info(msg,namespace=""):
    lua = ""
    if namespace != "": lua = f"(lua: {namespace})"
    createMessage(f"{colors.LBLUE}{lua}{colors.LGRAY} :: {msg}{colors.RESET}")

def warn(msg,namespace=""):
    lua = ""
    if namespace != "": lua = f"(lua: {namespace})"
    createMessage(f"{colors.LBLUE}{lua}{colors.YELLOW} ?? {msg}{colors.RESET}")

def err(msg,namespace=""):
    lua = ""
    if namespace != "": lua = f"(lua: {namespace})"
    createMessage(f"{colors.LBLUE}{lua}{colors.RED} !! {msg}{colors.RESET}")

def fatal(msg,exitCode=1):
    createMessage(f"{colors.RED}{'*'*32}")
    createMessage(f"A fatal error has occurred with the following message.")
    createMessage(f"{colors.RED}{'*'*32}")
    createMessage("")
    createMessage(f"{msg}{colors.RESET}")
    exit(exitCode)