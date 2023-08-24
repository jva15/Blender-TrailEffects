bl_info = {
    "name": "TrailPlanTest",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import os
import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import time
import pdb#for pdb.trace()

def add_material(self,context,Uflip=True,Vflip=False):
    
    trailshader=bpy.data.materials.new(name="Trail Shader Test")
    
    #if it already exist, make another with a new name
    wi=0
    while(trailshader==False):
        wi+=1
        bpy.data.materials.new(name=f'Trail Shader Test.{wi:03}')
    ts=trailshader
    ts.use_nodes=True
    fnewnode=ts.node_tree.nodes.new
    
    #remove the principled for  a nice blank slate
    ts.node_tree.nodes.remove(ts.node_tree.nodes.get('Principled BSDF'))
    #where our nodes output
    material_output =ts.node_tree.nodes.get('Material Output')
    
    
    #just a set of actions that i indend to put on all nodes
    def Generic_Node_Setup(node):
        node.hide=True
        node.select=False
        return node
    def MakeNode(node_data):#convert custom node data container to actual node, no connections yet
        name=node_data[0]
        data=node_data[1]
        print(data)
        newnode=fnewnode(name)
        
        
        if name=='ShaderNodeValToRGB':
            elements=newnode.color_ramp.elements
            elements.remove(elements[0])
            remove_end=False#since i can't just delete both at the beggining, I'll use this variable to make sure i don't delete elements that were placed by the user.
            
            for k,v in data.items():
                element=elements.new(k)
                if (not remove_end) and k==1.0:
                    remove_end=True
                element.color=v
            if remove_end:
                elements.remove(elements[len(elements)-1])
                
        elif name=='ShaderNodeTexImage':
            for k,v in data.items():
                if k=='image':
                    newnode.image=bpy.data.images[v]
        elif name=="ShaderNodeValue":
            for k,v in data.items():
                newnode.outputs[k].default_value=v
        
        
        else:#all other nodes
            for k,v in data.items():
                if k=='o':
                    newnode.operation=v
                elif k=='bt':
                    newnode.blend_type=v
                elif k=='data_type':
                    newnode.data_type=v
                else:
                    newnode.inputs[k].default_value=v
            
        
        
        return Generic_Node_Setup(newnode)
        
    
    
    
    
    lanes=[]
    nlinks=[]#just simple links
    nodelanes=[]
    '''
    make an array of lanes
    this is mostly to make it easier to sort them to mantain some semblenc of order in the node editor
    each lane contains a list of sets. each set holding a the type name and a dictionary.
    Dictionary processing depends on the MakeNode Function.
    
    as for nlinks:
        each set defines(lane it is on,index within said lane,input-or-output)
            the first set is always the output
            later are inputs
    
    '''
    
    #0
    lanes.append([('ShaderNodeUVMap',{})])
    nlinks.append([(0,0,0),
    (3,0,0),(3,1,0),(5,1,6)]
    )
    #1
    lanes.append([('ShaderNodeValue',{0:-0.063})])
    nlinks.append([(1,0,0),
    (2,0,0),(2,1,0)])
    #2
    lanes.append([('ShaderNodeCombineXYZ',{}),
     ('ShaderNodeMath',{'o':'MULTIPLY',1:1.1}),#operations
     ('ShaderNodeCombineXYZ',{})])
    nlinks.append([(2,0,0),(3,0,1)
    ])
    nlinks.append([(2,1,0),(2,2,0)
    ])
    nlinks.append([(2,2,0),(3,1,1)
    ])
    #3
    lanes.append([('ShaderNodeMapping',{}),('ShaderNodeMapping',{3:(1.0,1.4,1.0)})])   
    nlinks.append([(3,0,0),(5,0,6)])
    nlinks.append([(3,1,0),(4,1,0)])
    
    #4
    lanes.append([('ShaderNodeTexNoise',{2:2.1}),('ShaderNodeTexNoise',{2:2.1,5:0.35})])
    nlinks.append([(4,0,1),(5,0,7)])
    nlinks.append([(4,1,1),(5,1,7)])
    
    #5  Note: output changes based on mode: Float: 0, Vector:1,Color2
    #lanes.append([('ShaderNodeMix',{0:0.167}),('ShaderNodeMix',{0:0.125})])
    lanes.append([('ShaderNodeMix',{0:0.167,'data_type':'RGBA'}),('ShaderNodeMix',{0:0.125,'data_type':'RGBA'})])
    nlinks.append([(5,0,2),(6,2,0)])
    nlinks.append([(5,1,2),(6,2,0)])
    
    
    
    #script_file = os.path.realpath(__file__)
    #directory = os.path.dirname(script_file)
    #for mod in addon_utils.modules():
    #if mod.bl_info['name'] == bl_info['name']:
    #    filepath = mod.__file__
    #    print (filepath)
    #else:
    #    pass
    #bpy.utils.user_resource('SCRIPTS', "addons")
    
    trailtex=bpy.data.textures.new("Trail_Texture","IMAGE")
    trailtex.image=bpy.data.images.load(imagefilepath+'/default_trail_texture.png')
    
    
    trailmask=bpy.data.textures.new("Trail_Mask","IMAGE")
    trailmask.image=bpy.data.images.load(imagefilepath+'/default_trail_mask.png')
    
    trailtex.image.source='FILE'
    trailmask.image.source='FILE'
    
    
    
    #ommitted note: wth is the point of naming if the naems cant be used...
    #bpy.data.images["Trail_Texture"].source = 'FILE'
    #bpy.data.images["Trail_Mask"].source = 'FILE'

    
    #should we flip the texture
    if Uflip:Uaxis=-1.0
    else:Uaxis=1.0
    if Vflip:Vaxis=-1.0
    else:Uaxis=1.0
    #mapping nodes
    nlinks.append([(6,2,0),(6,0,0)])
    nlinks.append([(6,2,0),(6,1,0)])
    
    
    
    
    #6 images lanes
    lanes.append([('ShaderNodeTexImage',{'image':"default_trail_texture.png"}),
    ('ShaderNodeTexImage',{'image':"default_trail_mask.png"}),
    ('ShaderNodeMapping',{3:(Uaxis,Vaxis,1.0)})
    ])
    nlinks.append([(6,0,0),(7,0,7)])
    nlinks.append([(6,1,0),(7,0,6)])
    
    
    
    
    

    #7
    lanes.append([('ShaderNodeMix',{'data_type':'RGBA','bt':'MULTIPLY'})])
    nlinks.append([(7,0,2),(8,0,0)])
    nlinks.append([(7,0,2),(10,0,0)])
    #8
    lanes.append([('ShaderNodeMapRange',{}),
    ('ShaderNodeValToRGB',{0.095:(0, 0.00175162, 8.3513, 1),0.659:(0.0559311, 3.67363, 4.67565, 1),1.000:(1,1,1,1)})])
    nlinks.append([(8,0,0),(8,1,0)])
    nlinks.append([(8,1,0),(9,1,0)])
    
    #9
    lanes.append([('ShaderNodeBsdfTransparent',{}),('ShaderNodeEmission',{1:10})])
    nlinks.append([(9,0,0),(10,0,1)])
    nlinks.append([(9,1,0),(10,0,2)])
    #10
    lanes.append([('ShaderNodeMixShader',{})])
    nlinks.append([(10,0,0),'Out'])
    
    
    
    #create the nodes
    for node_array_data in lanes:
        _lanedata=[]
        for node_data in node_array_data:
            _lanedata.append(MakeNode(node_data))
    
        nodelanes.append(_lanedata)
    
    
    #now that we have the nodes, let's get them sorted
    #
    
    #just to short hand
    def nget(lane,number):
        return nodelanes[lane][number]
    link=ts.node_tree.links.new    
    
    #a helper function 
    def multilink(node1,outputnumber,node2,inputnumbers):
        for i in inputnumbers:
            link(node1[outputnumber],node2[i])
    #spacing being a set of coordinates(x,y)        
    def highest(a,b):
        if a >= b:
            return a
        else: 
            return b
    
    #sort the nodes so that each lane represents a collumn with the given spacing
    #note: hmm... this doesn't seem to work the way i intended
    def sort(spacing=(0,0),lanes=[]):
        x=0
        y=0
        
        for lane in lanes:
            highestdimx=x
            y=0
            for node in lane:
                node.location=(x,y)
                highestdimx=highest(node.dimensions[0],highestdimx)
                y+=node.dimensions[1]+spacing[1]
                
            x+=highestdimx+spacing[0]   
        
    sort((20,5),nodelanes)
    
    #Now we link them together
    for l in nlinks:#range(len(links)):
        node1=nget(l[0][0],l[0][1])#get first node
        output =l[0][2]
    
        for i in range(1,len(l)):
            if l[i] == 'Out':
                link(node1.outputs[output],material_output.inputs[0])
            else:    
                node2=nget(l[i][0],l[i][1])#get first node
                
                input =l[i][2]
                link(node1.outputs[output],node2.inputs[input])    
        
    trailshader.blend_method='BLEND'
    
    material_output.location=(400,0)
    
    return trailshader
    #ts.node_tree.nodes.add('name') "do an add and look at the type='name'"

def UVOrientate(self,context):
    
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project()
    
def add_trailPlane(self, context,divisions=2,height=2):
    subdivision_edge_factor=0.999
    
    #create, rotate, and apply rotation
    bpy.ops.mesh.primitive_plane_add(size=height, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, release_confirm=True)

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    bpy.ops.object.editmode_toggle()
    
    if divisions:
        #make loopcuts for each division
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":divisions, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":0, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":0, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})
    
        #Make additional loop cuts for the sides
        
    #front
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":4, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":-subdivision_edge_factor, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})
    #back
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":0, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":subdivision_edge_factor, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})
        

        
    #down
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":1, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":-subdivision_edge_factor, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})
    
    #up
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":10+divisions*3, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":subdivision_edge_factor, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})


        
        #notes: starting edge index seems to be unaffected by amount of edges interstingly

    #rotate the the uv's so that its divided along the U axis.
    UVOrientate(self,context)
    
    newmesh=context.selected_objects[0]
    bpy.ops.object.mode_set(mode='OBJECT')
    modifier=newmesh.modifiers.new(name='TrailSubdivision',type='SUBSURF')
    modifier.levels=3
    modifier.quality=3
    
    
    
    

    return context.selected_objects[0]


'''


equaly distributes bones on the yaxis based on count and dimmension.
if toggle is on, it will adjusts the heights for better management

'''    
def EditBoneAdjust(self, context,dimension=(1,1),wave_edit_bones=[],toggle=True):
    height=dimension[1]
    length=dimension[0]
    
    rootheight=height/4
    baselevel=-height/2
    maxtip=height/2
    rightside=length/2
    leftside=-length/2
    number_of_bones=len(wave_edit_bones)
    divisions=(number_of_bones-2)
    
    #we want the bone to gradually decrease in size linearly so we set a rate at which it sizes down
    #incrementation is the space between each bone
    if divisions>0:
        incrementation=length/(divisions+1)
        if toggle:
            sizedownrate=(height-rootheight)/(divisions+1)
        else:
            sizedownrate=0
    else:
        incrementation=0

    
    
    
    for i in range(number_of_bones):
        head=wave_edit_bones[i].head
        tail=wave_edit_bones[i].tail
        
        
        
        
        head.yz=((rightside-i*incrementation),(baselevel))
        tail.yz=((rightside-i*incrementation),(maxtip-sizedownrate*i))
        wave_edit_bones[i].select=True
    return wave_edit_bones




def add_SwordTrailBones(self, context,divisions=2,height=2,length=2):
    rootheight=height/4
    baselevel=-height/2
    maxtip=height/2
    rightside=length/2
    leftside=-length/2
    number_of_bones=2+divisions
    trailbone=[]
    
    if divisions>0:
        incrementation=length/(divisions+1)
        sizedownrate=(height-rootheight)/(divisions+1)
    else:
        incrementation=0
        
        
    armob=bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    arm=context.selected_objects[0].data
    arm.display_type='STICK'
    #bpy.ops.object.editmode_toggle()
    trailroot=arm.edit_bones[0]
    trailroot.name='trail root'
    trailroot.head.yz=((rightside),(baselevel))
    trailroot.tail.yz=((rightside),(baselevel+rootheight))
    trailroot.select=True
    
    
    
    for i in range(number_of_bones):
        bpy.ops.armature.bone_primitive_add()
        trailbone.append(arm.edit_bones[i+1])
        trailbone[i].name=f'trail wave.{i:03}'
        #trailbone[i].head.yz=((rightside-i*incrementation),(baselevel))
        #trailbone[i].tail.yz=((rightside-i*incrementation),(maxtip-sizedownrate*i))
        #trailbone[i].select=True
    
    trailbone=EditBoneAdjust(self, context,(length,height),trailbone,False)
    
    
    trailbone[0].parent=trailroot
        
    bpy.ops.object.editmode_toggle()
    armob=bpy.context.selected_objects[0]
    

    return armob
  

def parentBonesToMesh(armature,mesh):
    #Parent them with automatic weights
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    armature.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    
    
    '''
    NoArmatureMod=True
    for modifier in newmesh.modifiers:
        if (modifier.type == 'ARMATURE') :
            modifier.object=armature
            NoArmatureMod=False
    if NoArmatureMod:
        modifier=newmesh.modifiers.new(name='wave armature',type='ARMATURE')
        modifier.object=armature
    '''
'''
'''    

    
    
    

    
    
def add_object(self, context):
    scale_x = self.scale.x
    scale_y = self.scale.y

    verts = [
        Vector((-1 * scale_x, 1 * scale_y, 0)),
        Vector((1 * scale_x, 1 * scale_y, 0)),
        Vector((1 * scale_x, -1 * scale_y, 0)),
        Vector((-1 * scale_x, -1 * scale_y, 0)),
    ]

    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)






class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_testplane"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        blade_height=4
        div=8
        
        
        add_material(self,context)
        

        trailPlane=add_trailPlane(self,context,div,blade_height)
        bones=add_SwordTrailBones(self,context,div,blade_height,blade_height)
        parentBonesToMesh(bones,trailPlane)
        
        return {'FINISHED'}
def debugtest():
    print('11test')

# Registration

def add_object_button(self, context):
    print('add object test')
    print(OBJECT_OT_add_object.bl_idname)
    print(self.layout)
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Object",
        icon='PLUGIN')
    

'''
# This allows you to right click on a button and link to documentation
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping
'''    
    
    #bpy.data.texts['TrialPlaneTest.py']


fp=bpy.data.texts['TrailPlaneTests.py'].filepath
fa=fp.split('\\')
fa=fa[0:len(fa)-1]
fp='\\'.join(fa)
imagefilepath=fp+'\\images'
print(imagefilepath)


def register():
    #bpy.ops.script.reload() 
    script_file=os.path.realpath(__file__)
    print(os.path.dirname(script_file))
    #print(OBJECT_OT_add_object.bl_idname)
    
    bpy.utils.register_class(OBJECT_OT_add_object)
    #bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    print("file is")
    
    


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    #bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()
    
    
