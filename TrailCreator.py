bl_info ={
    "name": "Trail Tracer",
    "author" : "Geiger(aka jva15)",
    "version": (0,0,9),
    "blender": (3,6,0),
    "category": "Effects",
    "location":"View3D > Toolshelf",
    "description":"Creates a Trail based on a bone and a preset",
    }

import bpy
from bpy.props import *
import TrailPlaneTests as Generate




class TrailCreationPanel(bpy.types.Panel):
    bl_label="Sword Trail"
    bl_idname = "VIEW_3D_PT_SwordTrailPrototype"
    bl_space_type="VIEW_3D"
    bl_region_type='UI'
    bl_category = 'Effects'
    
    
    
    #mode=testenum
    Testnumber: FloatProperty(
        idname="Testnumber",
        name= "just a number",
        description="A numba is me",
        default=0.0,
        min=0.0
    )
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        mode=bpy.context.scene.TT_Trail_Mode_Enum
       
        row = layout.row()
        #if self.mode=='Generate':
        #    row.label(text= "Select Trail Object.")
        row = layout.row()
        row.prop(scene,"TT_Trail_Mode_Enum")
        
        
        
        if mode=='GEN':#todo
            print('')
            #row.label(text='gen')
            
            # A check box to select a material
                #if true display a list of materials
                #Select U or V
            #else use default material
            
            #generate Mesh, set to TrailMesh
            #generate armature, set to Trail Bones
            row = layout.row()
            row.prop(scene,"UFlip")
            row.prop(scene,"VFlip")
            
            
        elif mode=='LEG':
            row = layout.row()
            row.prop(scene, "TrailBones")
            row = layout.row()
            row.prop(scene, "TrailMesh")
        
        
            
        
        row = layout.row()
        row.prop(scene,"TrailWidth")
        
        row = layout.row()
        
        if (context.object and context.object.mode == 'POSE') and (len(bpy.context.selected_pose_bones) !=0):
            row.operator('object.strails')
        else:
            row.label(text= "Select a Bone to trace a trail on")
        
            
            
                
        #else self.mode==
        
        
        #row = layout.row(align=True)
        
        
        layout.label(text=" Bake Range :")
        row = layout.row(align=True)
        
        row.prop(scene, "Trailstartframe")
        row.prop(scene, "Trailendframe")
        row = layout.row()
        
        row = layout.row()
        row.prop(scene, "TrailFrameLength")
        row = layout.row()
       
def duplicate(obj, data=True, actions=True, collection=None):
    obj_copy = obj.copy()
    collection=bpy.context.view_layer.active_layer_collection.collection
    if data:
        obj_copy.data = obj_copy.data.copy()
    #if actions and obj_copy.animation_data:
    #    obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    collection.objects.link(obj_copy)
    return obj_copy

def Phase1():
    
    return 

def Phase2(obj):
    bpy.ops.object.posemode_toggle()
    
def NFString(str1,num):
    #if num==0:
    #    return str1
    #else:
    return str1+'.'+str(num).zfill(3)



class TrailCreationOperator(bpy.types.Operator):
    bl_label="SwordTrail"
    bl_idname="object.strails"
    bl_options = {'REGISTER','UNDO'} 
    NameOfBones="trail wave"    
    NameOfRoot="trail root"
    BoneCount=4
    beraseArm=True
    bakeoption=True
    divisions=BoneCount-2
    
    
    
    
    def execute(self, context):
        #if self.unlocked:
        #print(bpy.context.scene.TrailBones.data)
        #print(bpy.context.scene.TrailMesh)
        #bpy.context.scene.TrailBones.armature_add()
        
        ts=bpy.context.scene.tool_settings
        
        autokey=ts.use_keyframe_insert_auto
        ts.use_keyframe_insert_auto=False        
        
        
        makeCopy=False
        
        
        if bpy.context.selected_objects[0] is None:
            print("Error:selected Object is none")
            return
        if bpy.context.selected_objects[0].type != "ARMATURE":
            print("Error:selected Object is not armature")
            return
        if bpy.context.active_pose_bone is None:
            print("Error:No active pose bone")
            return
        
        
        
        targetArmature=bpy.context.selected_objects[0]
        SelectedBone=bpy.context.active_pose_bone
        
        
        #go to object mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        mode=bpy.context.scene.TT_Trail_Mode_Enum
        if mode=='GEN':
            print('Generating mesh and bones')
            TrailWidth=bpy.context.scene.TrailWidth
            bpy.context.scene.TrailMesh=Generate.add_trailPlane(self, context,divisions=self.divisions,height=TrailWidth)
        
            bpy.context.scene.TrailBones=Generate.add_SwordTrailBones(self, context,divisions=self.divisions,height=TrailWidth,length=TrailWidth)
        else:
            print('skipped generation')   
        
        if bpy.context.scene.TrailBones is None:
            print("Error:No Trail Bones")
            return
        if bpy.context.scene.TrailMesh is None:
            print("Error:No Trail Mesh")
            return
        
        
        #elif mode='LEG':
        
        
        
            
        
        
        #duplicate
        if makeCopy:
            #duplicate the armatur
            newarm=duplicate(
                obj=bpy.context.scene.TrailBones,
                data=True,
                actions=True
            )
        else:
            newarm=bpy.context.scene.TrailBones
            
        if makeCopy:    
            #duplicate Mesh
            newmesh=duplicate(
                obj=bpy.context.scene.TrailMesh,
                data=True,
                actions=True
            )
        else:
            newmesh=bpy.context.scene.TrailMesh
        
        if mode=='GEN':        
            
            #bpy.ops.object.mode_set(mode='OBJECT')
            
            
            newmesh.select_set(True)
            newmesh.data.materials.append(Generate.add_material(
            self,context,
            Uflip=bpy.types.Scene.UFlip,
            Vflip=bpy.types.Scene.VFlip))
            
            
            

            

        
        
        
        
        if mode=='GEN':
            #link the mesh to armature
            Generate.parentBonesToMesh(newarm,newmesh)
            newmesh.modifiers.move(0,1)
    
        if mode=='LEG':
            #link the mesh to armature
            if self.beraseArm:
                NoArmatureMod=True
                for modifier in newmesh.modifiers:
                    if (modifier.type == 'ARMATURE') :
                        modifier.object=newarm
                        NoArmatureMod=False
                if NoArmatureMod:
                    modifier=newmesh.modifiers.new(name='wave armature',type='ARMATURE')
                    modifier.object=newarm
        
        
        #select the armature and pose it            
        bpy.ops.object.select_all(action='DESELECT')
        newarm.select_set(True) 
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        
        
        #make sure nothing is selected
        bpy.ops.pose.select_all(action='DESELECT')
        
        #for each Bone, set a transform constraint
        for i in range(1,self.BoneCount):#add a transform moddifier to all the bone except the lead
            con=newarm.pose.bones[NFString(self.NameOfBones,i)].constraints.new(type='COPY_TRANSFORMS')
            con.target=newarm
            #con.subtarget=newarm.pose.bones[self.NameOfBones]
            #print('the bone is constraining to :'+NFString(self.NameOfBones,0))
            con.subtarget=NFString(self.NameOfBones,0)
            
        
        
        #bone.constraints.new('COPY_ROTATION')
        #or use copy location and copy rotation. I'll make that an option later
        #todo also parent swordwave to sword root later
        
        #then set the sword root to copy the transform of the moving target
        con=newarm.pose.bones[self.NameOfRoot].constraints.new(type='COPY_TRANSFORMS')
        con.target=targetArmature
        con.subtarget=SelectedBone.name
        
        
        #ok now the transformations are set
        
        #select the waves nodes and start bakin!
        #select
        bpy.ops.pose.select_all(action='DESELECT')#deselect all
        for i in range(self.BoneCount):
            newarm.pose.bones[NFString(self.NameOfBones,i)].bone.select=True
            
        #plug values    
        bakestart=bpy.context.scene.Trailstartframe
        bakeend=bpy.context.scene.Trailendframe
        #BakeOperation
        bpy.ops.nla.bake(frame_start=bakestart, frame_end=bakeend, visual_keying=True, clear_constraints=True, bake_types={'POSE'})
        
        
        #shift them all by the length
        timeconstant=1*bpy.context.scene.TrailFrameLength
        for i in range(self.BoneCount):
            bpy.ops.pose.select_all(action='DESELECT')#deselect all
            
            newarm.pose.bones[NFString(self.NameOfBones,i)].bone.select=True
            
            #bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(timeconstant*i, 0, 0, 0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            #shift the bones by their fcurves
            for a in range(0,10):
                curvslot=a+i*10
                curve=newarm.animation_data.action.fcurves[curvslot]
                
                if timeconstant>0:
                    for point in reversed(curve.keyframe_points):
                        if point is not None:
                            point.co[0]=point.co[0]+timeconstant*i
                else:
                    for point in curve.keyframe_points:
                        if point is not None:
                            point.co[0]=point.co[0]+timeconstant*i
                
        
        
        #return autokeying to normal
        ts.use_keyframe_insert_auto=autokey
        
        #return to the armature
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.context.area.ui_type = 'VIEW_3D'

        
        bpy.context.view_layer.objects.active=targetArmature
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
            
        return {'FINISHED'}
    

def filter_mesh_objects(self, object):
    return object.type == 'MESH'
def filter_amature_objects(self,object):
    return object.type == 'ARMATURE'

def register():
    bpy.types.Scene.TrailBones = PointerProperty(type=bpy.types.Object,poll=filter_amature_objects)
    bpy.types.Scene.TrailMesh = PointerProperty(type=bpy.types.Object,poll=filter_mesh_objects)
    #bpy.types.Scene.TrailCurve= PointerProperty(type=bpy.types.CurveMapping)
    
    
    bpy.types.Scene.TT_Trail_Mode_Enum= EnumProperty(
        name="Mode",
        default='GEN',
        
        description="",
        items=[('GEN','Generate',"Generates the Geometry")#,
        #('EXI','existing', "use existing one and make a copy. supposed to be more flexible than legacy"),
        #('Bend',"takes a piece of geometry, put the bones along it's length"),
        #('LEG','legacy',"old functionality. take an already made one and apply it")
        #('Stretch',"Sample a piece of geometry, subdivide")
        ]
    )
    bpy.types.Scene.TrailMaterialUVenum=EnumProperty(
        name='UV axis',
        default='U',
        description='determines axis the cuts are made along',
        items=[('U','U Axis',""),('V','V Axis',"")]
    )
    
    
    
    bpy.types.Scene.Trailstartframe= IntProperty(
        name= "StartFrame",
        description="The Frame the bake Starts at",
        default=0,
        min=0
    )
    bpy.types.Scene.Trailendframe= IntProperty(
        name="EndFrame",
        description="The Frame The Bake ends",
        default=250
    
    )
    bpy.types.Scene.TrailFrameLength=IntProperty(
        name="Frame Length",
        description="Frame length for each node to be pushed back",
        default=1
    
    )
    bpy.types.Scene.UFlip=BoolProperty(
        name="UFlip",
        description="Flip the Texture on it V axis",
        default=True
    )
    bpy.types.Scene.VFlip=BoolProperty(
        name="VFlip",
        description="Flip the Texture on it V axis",
        default=False
    )
    bpy.types.Scene.TrailWidth=FloatProperty(
        name='Trail Width',
        description="width of the trail",
        default=2.0
    )
    
    bpy.utils.register_class(TrailCreationOperator)
    bpy.utils.register_class(TrailCreationPanel)
    #TrailPlaneTests.debugtest()

def unregister():
    bpy.utils.unregister_class(TrailCreationPanel)
    bpy.utils.unregister_class(TrailCreationOperator)
    
    
    del bpy.types.Scene.TrailBones
    del bpy.types.Scene.TrailMesh
    del bpy.types.Scene.TT_Trail_Mode_Enum

if __name__ == "__main__":
    register()
