import bpy
import os
import sys
 
''' 

it will run the script on all modules(the ones listed in ini)
while also handling dependencies.

any file the imports modules from within the project will not know
you made changes to said modules unless you run this script. 

it reads the actual files so remember to save the files you edit before you run.
I recommend giving this its own small little window

'''
 
 
fp=bpy.data.texts['__init__.py'].filepath
fa=fp.split('\\')
fa=fa[0:len(fa)-1]
fp='\\'.join(fa)
fp='\\'+fp[2::]
print(fa) 
print(fp)
filesDir = fp#"d:/Python/TestMultifile"
 
initFile = "__init__.py"
 
if filesDir not in sys.path:
    sys.path.append(filesDir)
 
file = os.path.join(filesDir, initFile)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')
 
exec(compile(open(file).read(), initFile, 'exec'))
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')