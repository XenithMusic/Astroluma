import debug as d
import os
import copy
try:
    from lupa import lua52 as lupa
except ImportError:
    import lupa
import const
import psutil
import assets
import settings
import registrations
import nodes
import jsonc

ass = None
cfg = None
currentNamespace = None

def currentRuntime() -> lupa.LuaRuntime:
    global contexts,currentNamespace
    return contexts[currentNamespace]

def pythonize_lua_table(tbl):
    result = {}
    for i,v in tbl.items():
        if "Table" in str(type(v)):
            v = pythonize_lua_table(v)
        result[i] = v
    return result

"""
Errors
"""

ERR_UNSAFE_FETCH = "Flagged an unsafe %s fetch! %s"
ERR_UNSAFE_ASSET_CATEGORY = ERR_UNSAFE_FETCH % ("asset","Category '%s' not pre-approved.")
ERR_UNSAFE_DATA_TYPE = ERR_UNSAFE_FETCH % ("asset","Couldn't sanitize data type of '%s:%s'")

ERR_MOD_CONFLICT = "Mod conflict! %s"
ERR_REGISTRATION = ERR_MOD_CONFLICT % f"Mod '%s' tried to register setting %s key '%s' already defined by mod '%s'!"

"""

Lupa API

"""

def lua_assert(true):
    assert true

def lua_print(msg):
    global currentNamespace
    d.info(msg,currentNamespace)

def lua_warn(msg):
    global currentNamespace
    d.warn(msg,currentNamespace)

def lua_error(msg):
    global currentNamespace
    d.err(msg,currentNamespace)

def lua_assets_get(category,key):
    global ass
    safe_categories = [
        "scripts",
        "locale",
        "shaders",
        "fonts"
    ]
    if not category in safe_categories:
        lua_warn(ERR_UNSAFE_ASSET_CATEGORY % category)
        return None
    try:
        unsafe = getattr(ass,category)[key]
    except KeyError as e:
        lua_error(f"Failed to get asset with key `{key}`.")
        raise e
    if isinstance(unsafe,assets.Locale):
        return {
            "type":"locale",
            "name":unsafe.name,
            "keys":dict(unsafe.keys)
        }
    elif isinstance(unsafe,assets.ShaderContent):
        return {
            "type":"shader",
            "content":unsafe.code
        }
    elif isinstance(unsafe,assets.Font):
        raise TypeError("Fonts are not supported through game.assets.get. Please use the game.assets.font methods.")
    elif isinstance(unsafe,str):
        return copy.deepcopy(unsafe)
    elif isinstance(unsafe,list):
        return copy.deepcopy(unsafe)
    lua_warn(ERR_UNSAFE_DATA_TYPE % (category,key))
    raise PermissionError("Unsafe asset fetch")

def lua_settings_get():
    return copy.deepcopy(cfg.dict)
def lua_settings_set(settings):
    if not "input" in currentRuntime()[2]:
        d.fatal("Unsafe mod; attempt to write settings without user input!")
    settings = pythonize_lua_table(settings)
    for i,v in settings.items():
        cfg.dict[i] = v
def lua_settings_register(key,default):
    if key in registrations.settings:
        d.fatal(ERR_REGISTRATION % (currentNamespace,"setting",key,registrations.settings[key][0]))
    registrations.settings[key] = (currentNamespace,default)

def lua_menu_register(key,initHook,children,prerenderHook=lambda shared,offsetX,offsetY: 0,renderHook=lambda shared,offsetX,offsetY: 0,
                      postrenderHook=lambda shared,offsetX,offsetY: 0):
    if key in registrations.menus:
        d.fatal(ERR_REGISTRATION % (currentNamespace,"menu",key,registrations.menus[key][0]))
    def init_fn(self):
        self.shared = {}
        self.luafn = {"children":children,"init":initHook,"prerender":prerenderHook,"render":renderHook,"postrender":postrenderHook}
        super(nodes.LuaScene,self).__init__()
    MenuType = type(f"lua_dynamenu_{key}",
            (nodes.LuaScene,),
            {
                "__init__":init_fn
            }
        )
    registrations.menus[key] = (currentNamespace,MenuType)

def lua_menu_override(original,replacement):
    registrations.menuOverrides[original] = replacement

contexts = {
    # "astroluma":lupa.LuaRuntime(
    #     unpack_returned_tuples=True,
    #     register_eval=False,
    #     register_builtins=False
    # )
}

def create_context(namespace,env=None,context=None):
    contexts[namespace] = [
        lupa.LuaRuntime(
            unpack_returned_tuples=True
        ),
        None,
        None
    ]
    if env == None:
        env = create_environment(contexts[namespace][0],namespace)
    if context == None:
        context = ["base"]
    replace_context_env(namespace,env,context)
    return contexts[namespace]

def create_environment(runtime:lupa.LuaRuntime,namespace):
    lt = runtime.table
    base_env = lt()

    # Base lua

    base_env["math"] = runtime.globals().math
    base_env["string"] = runtime.globals().string
    base_env["table"] = runtime.globals().table
    base_env["coroutine"] = runtime.globals().coroutine
    base_env["utf8"] = runtime.globals().utf8
    base_env["type"] = runtime.globals().type
    base_env["pairs"] = runtime.globals().pairs
    base_env["ipairs"] = runtime.globals().ipairs
    base_env["next"] = runtime.globals()["next"]
    base_env["select"] = runtime.globals().select
    base_env["print"] = lua_print
    base_env["warn"] = lua_warn
    base_env["error"] = lua_error
    base_env["assert"] = lua_assert
    base_env["pcall"] = runtime.globals().pcall
    base_env["xpcall"] = runtime.globals().xpcall
    base_env["tostring"] = runtime.globals().tostring
    base_env["tonumber"] = runtime.globals().tonumber
    base_env["os"] = lt()
    base_env["os"]["clock"] = runtime.globals().os.clock
    base_env["os"]["time"] = runtime.globals().os.time
    base_env["os"]["date"] = runtime.globals().os.date
    base_env["os"]["difftime"] = runtime.globals().os.difftime
    base_env["bit32"] = runtime.globals().bit32
    base_env["_VERSION"] = runtime.globals()._VERSION
    base_env["_G"] = runtime.eval("nil")
    base_env["_NAMESPACE"] = namespace
    base_env["_CONTEXT"] = ["base"]

    # Astroluma API

    """
        `game` is an API allowing you to access stuff that isn't specific to gameplay.
    """
    base_env["game"] = lt()

    """
        `game.assets` is an API allowing you to access assets.
    """

    base_env["game"]["assets"] = lt()
    base_env["game"]["assets"]["get"] = lua_assets_get

    """
        `game.settings` is an API allowing you to access settings.
    """

    base_env["game"]["settings"] = lt()
    base_env["game"]["settings"]["get"] = lua_settings_get
    base_env["game"]["settings"]["set"] = lua_settings_set
    base_env["game"]["settings"]["register"] = lua_settings_register

    """
        `game.menu` is an API allowing you to register, override, and create menus.
    """

    base_env["menu"] = lt()
    base_env["menu"]["register"] = lua_menu_register
    base_env["menu"]["override"] = lua_menu_override

    return base_env

def replace_context_env(namespace,env,context=None):
    global contexts
    contexts[namespace][1] = env
    if context:
        contexts[namespace][2] = context

def execute_sandbox(code,namespace,assets,context=["base"],allowExit=True):
    global currentNamespace
    currentNamespace = namespace
    runtime = contexts[namespace][0]
    env = contexts[namespace][1]
    env["_CONTEXT"] = context
    contexts[namespace][2] = context
    loader = runtime.eval(assets.scripts["loader"])
    success,result = loader(code,env)
    if success == False:
        if isinstance(result,SystemExit) and allowExit:
            exit(result.code)
        else:
            lua_error(repr(result))
    currentNamespace = None
    env["_CONTEXT"] = ["base"]
    contexts[namespace][2] = ["base"]
    return success,result

def executef_sandbox(file,namespace,assets,context=["base"],allowExit=True):
    with open(file,"r") as f:
        data = f.read()
    return execute_sandbox(data,namespace,assets,context,allowExit)

max_malloc = psutil.virtual_memory().total/4
max_malloc = min(512*const.SIZE_MB,max_malloc)



"""
Loader
"""

def init(assets,settings):
    global ass,cfg
    ass = assets
    cfg = settings

class Mod:
    def __init__(self,path):
        self.path = path
        with open(self.path + "/mod.json","r") as f:
            self.json = jsonc.loads(f.read())
        self.namespace = self.json["name"]
        self.script_paths = [self.path + "/scripts/" + x for x in os.listdir(self.path + "/scripts")]
        self.scripts = {}
        for i in self.script_paths:
            name = i.split("/")[-1].replace(".lua","")
            with open(i,"r") as f:
                self.scripts[name] = f.read()
        create_context(self.namespace)
    def run_script(self,name,context):
        return execute_sandbox(self.scripts[name],self.namespace,ass,context)

def discover_mods():
    mods = [Mod(f"mods/{x}") for x in os.listdir("mods/")]
    if len(mods) != 0:
        d.warn("Game is modded! Unstable behavior may not necessarily be the fault of the developer!")
        d.info(f"Found {len(mods)} mods")
    return mods

if __name__ == "__main__":
    cfg = settings.Settings()
    ass = assets.Assets(displaying=False)
    d.debug("Testing mod loader.",0)
    d.debug("Test 1 : creating context")
    d.debug("Test 1a: making sure contexts is empty first",2)
    assert(contexts == {})
    create_context("astroluma",{"randomInteger":1,"assert":lua_assert,"print":lua_print},["base"])
    d.debug("Test 1b: making sure it actually made a context",2)
    assert(contexts != {})
    d.debug("Test 1c: making sure context is valid",2)
    assert(contexts["astroluma"][1]["randomInteger"] == 1)



    d.debug("Test 2 : running anything with that context")
    result = execute_sandbox("assert(randomInteger==1);print('the code works!')","astroluma",ass)
    print(result)
    assert(result[0] == True)



    d.debug("Test 3 : making a new context with a proper env")
    d.debug("Test 3a: making sure it doesnt exist already",2)
    assert(not "mod1" in contexts)
    create_context("mod1",{},["base"])
    replace_context_env("mod1",create_environment(contexts["mod1"][0],"mod1"))
    d.debug("Test 3b: making sure it exists now",2)
    assert("mod1" in contexts)



    d.debug("Test 4 : properly use the new context")
    d.debug("Test 4a: first, make sure that the setting for 'locale' is en_US",2)
    assert(cfg.dict["locale"] == "en_US")
    result = executef_sandbox("assets/scripts/silly.lua","mod1",ass,context=["input"])
    print(result)
    d.debug("Test 4b: check if it succeeded",2)
    assert(result[0] == True)
    d.debug("Test 4c: check if it returned the 'gui.menu.fire' locale key in german.",2)
    assert(result[1] == "FEUER")
    d.debug("Test 4d: check if it changed the locale to german.",2)



    assert(cfg.dict["locale"] == "de_DE")
    d.debug("Test 5 : Attempting illegal settings change")
    d.debug("Test 5a: first, make sure that the setting for 'locale' is de_DE",2)
    assert(cfg.dict["locale"] == "de_DE")
    result = executef_sandbox("assets/scripts/silly.lua","mod1",ass,context=["base"],allowExit=False)
    print(result)
    d.debug("Test 5b: check if it failed",2)
    assert(result[0] == False)
    d.debug("Test 5c: make sure that the setting for 'locale' is still de_DE",2)
    assert(cfg.dict["locale"] == "de_DE")



    d.debug("Test 6 : make a menu!",2)
    d.debug("Test 6a: first, make sure that it's not already a thing",2)
    assert(not "gob" in registrations.menus)
    result = executef_sandbox("assets/scripts/silly.lua","mod1",ass,context=["menu"])
    print(result)
    d.debug("Test 6b: make sure it IS a thing now",2)
    assert("gob" in registrations.menus)
    result = executef_sandbox("assets/scripts/silly.lua","mod1",ass,context=["menu"],allowExit=False)
    d.debug("Test 6c: check if overwriting it failed",2)
    assert(result[0] == False)
    print(result)