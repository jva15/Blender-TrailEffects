bl_info ={
    "name": "TrailTracer",
    "author" : "Geiger(aka jva15)",
    "version": (0,0,5),
    "blender": (3,6,0),
    "category": "Effects",
    "location":"View3D > Toolshelf",
    "description":"Creates a Trail based on a bone and a preset",
    }
import bpy


modulesNames = ['TrailCreator', 'TrailPlaneTests']
 
import sys
import importlib
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
if __name__ == "__main__":
    register()
'''
if "bpy" in locals():
    import importlib
    importlib.reload(TrailCreator)
    importlib.reload(TrailPlaneTests)
else:
    from . import TrailCreator
    from . import TrailPlaneTests



def register():
    print("")
def unregister():
    print("")'''
    
    
