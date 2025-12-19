import json

def loads(str,*a,**b):
    list = str.split("\n")
    list = [x.split("//")[0].rstrip() for x in list]
    nstr = "".join(list)
    return json.loads(nstr,*a,**b)
def load(f,*a,**b):
    return loads(f.read(),*a,*b)
def dumps(*a,**b):
    json.dumps(*a,**b)
def dump(*a,**b):
    json.dump(*a,**b)