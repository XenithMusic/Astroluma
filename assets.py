import os
from raylib import *
from cffi import FFI
ffi = FFI()
NULL = ffi.NULL
def parse_asset(file_path,key=""):
    """
    This function parses an asset file and returns a useful object.
    Replace this with actual parsing logic based on your asset types.
    """
    # Placeholder logic: Just return the file path for now.
    if file_path.endswith(".ttf"):
        font = LoadFontEx(file_path.encode(),120,NULL,0)
        return font
    if file_path.endswith(".mp3"):
        if "music" in key:
            sfx = LoadMusicStream(file_path.encode())
        else:
            sfx = LoadSound(file_path.encode())
        return sfx
    if file_path.endswith("_frag.glsl"):
        shader = LoadShader(NULL,file_path.encode())
        return shader
    if file_path.endswith("_vertex.glsl"):
        shader = LoadShader(file_path.encode(),NULL)
        return shader

    with open(file_path,"r") as f:
        return f.read()

def collect_assets(folder_path, namespace=None, parent_key=""):
    """
    Recursively collect all assets from a folder and subfolders.
    
    Args:
        folder_path (str): The path to the folder to scan.
        namespace (str): The namespace that the folder should be assigned.
        parent_key (str): The parent key for recursive subfolder keys.

    Returns:
        dict: A dictionary of assets.
    """
    if namespace == None: namespace = "astrolume"

    assets = {}

    # Iterate over all the items in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isdir(item_path):
            # If it's a directory, recurse into it
            new_key = f"{namespace}:{parent_key}.{item}" if parent_key else item
            assets.update(collect_assets(item_path, namespace, new_key))
        else:
            # If it's a file, parse the asset and add to the dictionary
            key = f"{namespace}:{parent_key}.{".".join(item.split(".")[:-1])}" if parent_key else item
            assets[key] = parse_asset(item_path,key)

    return assets
def destroy_assets(assets):
    for i in assets.values():
        if "struct Font" in repr(i):
            print("Unloaded font.")
            UnloadFont(i)
        if "struct Sound" in repr(i):
            print("Unloaded sound.")
            UnloadSound(i)
        if "struct Music" in repr(i):
            print("Unloaded music stream.")
            UnloadMusicStream(i)
        if "struct Shader" in repr(i):
            print("Unloaded shader.")
            UnloadShader(i)