import bpy
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)
from mathutils.bvhtree import BVHTree
from mathutils import (
    Vector,
    Matrix,
)
from collections import deque
from math import (
    pow, cos,
    pi, atan2,
)
from random import (
    random as rand_val,
    seed as rand_seed,
)
import time

import bmesh
import math
import mathutils
from bpy.types import Menu, Panel, UIList
from bpy.props import FloatVectorProperty, FloatProperty
from mathutils import Vector
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

bl_info = {
    "name": "SuperTools",
    "author": "Tim Gregory",
    "version": (0, 1, 1),
    "blender": (4, 00, 0),
    "location": "View3D > Sidebar > Super Tools (Create Tab)",
    "description": "Simplified UI for disabled users"
}

# UTILITY FUNCTIONS

def move(myx, myy, myz):
    print('move..', myx, myy, myz)
    myVec = Vector((myx, myy, myz))
    bpy.ops.transform.translate(value=(myx, myy, myz))


def extrude(myx, myy, myz):
    myVec = Vector((myx, myy, myz))
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror": False}, TRANSFORM_OT_translate={"value": myVec})

def updatepropsize(self,context):
    print('updating...')
    scene = context.scene
    scene.tool_settings.proportional_size=scene.key_floatpropsize
    print(scene.tool_settings.proportional_size)

def calcMedianPoint():
    print('median')

def scaleMesh(self,context):
    scene = context.scene
    superProps = context.window_manager.super_tools_props
    
    current_mode = bpy.context.object.mode

    inobjectmode = True
    if current_mode == 'EDIT':
        inobjectmode = False
        print('editmode')
    if current_mode == 'OBJECT':
        inobjectmode = True
        print('objectmode')
    obj = bpy.context.edit_object
    if inobjectmode:
        bpy.ops.object.mode_set(mode='EDIT')

        ob = bpy.context.edit_object
        mesh = bmesh.from_edit_mesh(ob.data)
        selected_indices = []
        for v in mesh.verts:
            if v.select:
                selected_indices.append(v.index)
              
            v.select = True
        # need to set back to object mode afterwards, at the nd

    print('scling')
    obj = bpy.context.edit_object
    mirrorexists = False
    for modifier in obj.modifiers:
     if modifier.type == 'MIRROR':
          mirrorexists = True
    fusedatcenter = False
    threshhold = .001
    
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    xtotal = 0
    ytotal = 0
    ztotal = 0
    count = 0
    selectedverts  = []
    for v in bm.verts:
        if (v.select):
            xtotal += v.co.x
            ytotal += v.co.y
            ztotal += v.co.z
            count += 1
            if ((v.co.x < threshhold) and (v.co.x > (-1.0*threshhold))):
               fusedatcenter = True
               
            #print(v.co.x)
            selectedverts.append(v)
    if (mirrorexists and fusedatcenter):
     for v in bm.verts:
        if (v.select):
            xtotal += -1.0 * v.co.x  #COUNT NEGATIVE X VALUES(SIMPLE VERSION FOR X MIRROR ONLY, NOT Y OR Z)
            ytotal += v.co.y
            ztotal += v.co.z
            count += 1
            #print(v.co.x)
            #selectedverts.append(v)
     
    
    if count==0:
        count =1
    medianpoint = ((-1*xtotal/count),(-1*ytotal/count),(-1*ztotal/count))
    print('med',medianpoint)
        #v.co.x += 1.0
    #mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
    print(superProps.key_median)
    #if (scene.key_median == "False"):
    if ((superProps.key_median == 0)):
        print('cursor!!!!')
        #medianpoint = (bpy.context.scene.cursor_location[0],bpy.context.scene.cursor_location[1],bpy.context.scene.cursor_location[2])
        medianpoint = (bpy.context.scene.cursor.location[0],bpy.context.scene.cursor.location[1],bpy.context.scene.cursor.location[2])


    mat_loc = mathutils.Matrix.Translation(medianpoint)
    print('cur',scene.cursor.location[0])
    #scale = mathutils.Vector((1.01,1.01,1.01))
    xs = 1.0
    ys = 1.0
    zs = 1.0
    try:
        xs = superProps.key_floatxs
    except:
        superProps.key_floatxs  = 1.0
    try:
        ys = superProps.key_floatys
    except:
        superProps.key_floatys  = 1.0
    try:
        zs = scene.key_floatzs
    except:
        superProps.key_floatzs  = 1.0
    
    
    
    scale = mathutils.Vector((xs,ys,zs))
    
    #scale = mathutils.Vector((1.0,1.0,1.0))
    bmesh.ops.scale(
        bm,
        vec=scale,
        space=mat_loc,
        verts=selectedverts
        )        
    
    if inobjectmode:
        for v in bm.verts:
            v.select = False
            if v.index in selectedverts:
                v.select = True
        #bpy.ops.object.mode_set(mode='OBJECT')
        

    bm.verts.index_update()
    print(selectedverts)
    bmesh.update_edit_mesh(me)
    if inobjectmode:
        bpy.ops.object.mode_set(mode='OBJECT')
    #bmesh.update_edit_mesh(me, True)
    


class OBJECT_OT_my_operator_gx1(bpy.types.Operator):
    bl_idname = "object.my_operator_gx1"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "UI"

    def execute(self, context):
        gx = 1.00
        superProps = context.window_manager.super_tools_props

        try:
            gx = superProps.key_floatmoveunit
        except:
            superProps.key_floatmoveunit = 1.00
        
        move(gx, 0.0, 0.0)
        return {'FINISHED'}

class OBJECT_OT_my_operator_gy1(bpy.types.Operator):
    bl_idname = "object.my_operator_gy1"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "UI"

    def execute(self, context):
        gy = 1.00
        superProps = context.window_manager.super_tools_props
        try:
            gy = superProps.key_floatmoveunit
        except:
            superProps.key_floatmoveunit = 1.00

        move(0.0, gy, 0.0)
        return {'FINISHED'}

class OBJECT_OT_my_operator_gz1(bpy.types.Operator):
    bl_idname = "object.my_operator_gz1"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "UI"

    def execute(self, context):
        gz = 1.00
        superProps = context.window_manager.super_tools_props
        try:
            gx = superProps.key_floatmoveunit
        except:
            superProps.key_floatmoveunit = 1.00

        move(0.0, 0.0, gz)
        return {'FINISHED'}


class OBJECT_OT_my_operator_emulate(bpy.types.Operator):
    bl_idname = "object.my_operator_emulate"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
       
    def execute(self,context):
     scene = context.scene
     print('Emulate')
     
     currentstate = bpy.context.preferences.inputs.use_mouse_emulate_3_button
     print(currentstate)
     tempstate = True
     if currentstate == True:
          tempstate = False
     if currentstate == False:
          tempstate = True
     currentstate = tempstate
     bpy.context.preferences.inputs.use_mouse_emulate_3_button = currentstate
     currentstate = bpy.context.preferences.inputs.use_mouse_emulate_3_button
     print(currentstate)
     return{'FINISHED'} 

class OBJECT_OT_my_operator_move(bpy.types.Operator):
    bl_idname = "object.my_operator_move"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        superProps = context.window_manager.super_tools_props
        #scene = context.scene
        #scene.update()
        key_floatxg = 1.11
        key_floatyg = 2.22
        key_floatzg = 3.33
        try:
            key_floatxg = superProps.key_floatxg
        except:
            scene.key_floatxg  = 0.0
        try:
            key_floatyg = superProps.key_floatyg
        except:
            scene.key_floatyg  = 0.0
        try:
            key_floatzg = superProps.key_floatzg
        except:
            superProps.key_floatzg  = 0.0
       
        myx = superProps.key_floatxg
        myy = superProps.key_floatyg
        myz = superProps.key_floatzg
    
        move(myx,myy,myz)
        return{'FINISHED'} 

class OBJECT_OT_my_operator_resetmove(bpy.types.Operator):
    bl_idname = "object.my_operator_resetmove"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        superProps = context.window_manager.super_tools_props
        #scene = context.scene
        #scene.update()
        superProps.key_floatxg  = 0.0
        superProps.key_floatyg  = 0.0
        superProps.key_floatzg  = 0.0
        return{'FINISHED'}

class OBJECT_OT_my_operator_ex1(bpy.types.Operator):
    bl_idname = "object.my_operator_ex1"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
       
    def execute(self,context):
        print('ex1')
        extrude(1.0,0.0,0.0)
        return{'FINISHED'}  


class OBJECT_OT_my_operator_ey1(bpy.types.Operator):
    bl_idname = "object.my_operator_ey1"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        print('ey1')
        extrude(0.0,1.0,0.0)
        return{'FINISHED'}  
    
class OBJECT_OT_my_operator_ez1(bpy.types.Operator):
    bl_idname = "object.my_operator_ez1"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        #scene = context.scene
        
        print('ez1')
        extrude(0.0,0.0,1.0)
        return{'FINISHED'}

class OBJECT_OT_my_operator_rx45(bpy.types.Operator):
    bl_idname = "object.my_operator_rx45"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"  
    def execute(self,context):
        print('rx45')
        scene = context.scene
        rotate(0.785398,1.0,0.0,0.0) #45 degrees on x axis (Angle is in radians)
        return{'FINISHED'}

class OBJECT_OT_my_operator_ry45(bpy.types.Operator):
    bl_idname = "object.my_operator_ry45"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"  
    def execute(self,context):
        print('ry45')
        scene = context.scene
        rotate(0.785398,0.0,1.0,0.0) 
        return{'FINISHED'}

class OBJECT_OT_my_operator_rz45(bpy.types.Operator):
    bl_idname = "object.my_operator_rz45"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"  
    def execute(self,context):
        print('rz45')  
        rotate(0.785398,0.0,0.0,1.0) 
        return{'FINISHED'}

class OBJECT_OT_my_operator_exact(bpy.types.Operator):
    bl_idname = "object.my_operator_exact"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
#        scene = context.scene
#        scene.update()

        superProps = context.window_manager.super_tools_props
        
        key_floatx = 1.11
        key_floaty = 2.22
        key_floatz = 3.33
        try:
            key_floatx = superProps.key_floatx
        except:
            scene.key_floatx  = 0.0
        try:
            key_floaty = superProps.key_floaty
        except:
            superProps.key_floaty  = 0.0
        try:
            key_floatz = superProps.key_floatz
        except:
            superProps.key_floatz  = 0.0
       
        myx = superProps.key_floatx
        myy = superProps.key_floaty
        myz = superProps.key_floatz
    
        extrude(myx,myy,myz)
        return{'FINISHED'}

class OBJECT_OT_my_operator_reset(bpy.types.Operator):
    bl_idname = "object.my_operator_reset"
    bl_label = "Super Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        superProps = context.window_manager.super_tools_props
#        scene = context.scene
#        scene.update()
        superProps.key_floatx  = 0.0
        superProps.key_floaty  = 0.0
        superProps.key_floatz  = 0.0
        return{'FINISHED'}

class OBJECT_OT_my_operator_resetscale(bpy.types.Operator):
    bl_idname = "object.my_operator_resetscale"
    bl_label = "Super Move"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        superProps = context.window_manager.super_tools_props
        superProps.key_floatxs  = 1.00
        superProps.key_floatys  = 1.00
        superProps.key_floatzs  = 1.00
        return{'FINISHED'}

class OBJECT_OT_my_operator_scale(bpy.types.Operator):
    bl_idname = "object.my_operator_scale"
    bl_label = "Super Scale"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "TOOLS"
    
    def execute(self,context):
        scaleMesh(self,context)
        #scene = context.scene
        #scene.update()
        calcMedianPoint()
        # BMESH --------------------------------------------
        #obj = bpy.context.edit_object
        #me = obj.data
        #bm = bmesh.from_edit_mesh(me)
        #for v in bm.verts:
        #    v.co.x += 1.0
        #bm.verts.index_update()
        #bmesh.update_edit_mesh(me, True)
        return{'FINISHED'}


##############################################################3333
class CURVE_PT_SuperToolsPanel(Panel):
    bl_label = "Super Panel"
    bl_idname = "CURVE_PT_SuperToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Super Tools"
    #bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}



    def draw(self, context):
        layout = self.layout
        wm = context.window_manager


        #col = layout.column(align=True)
        
        #col.label(text="ST:")


        toprow = layout.row()
        col0 = layout.column(align=True)
        currstate = bpy.context.preferences.inputs.use_mouse_emulate_3_button
        emulatetext = '?'
        if currstate == True:
          emulatetext = '(Currently Enabled)'
        if currstate == False:
          emulatetext = '(Currently Disabled)'
          
        #col0.label(text=emulatetext)
        if currstate == False:
          mytext = "Enable 3 Button" + emulatetext
          col0.operator("OBJECT_OT_my_operator_emulate",text=mytext,icon="COLORSET_03_VEC")
        if currstate == True:
          mytext = "Disable 3 Button" + emulatetext
          col0.operator("OBJECT_OT_my_operator_emulate",text=mytext,icon="COLORSET_03_VEC")
        

        col = layout.column(align=True)
        col.prop(wm.super_tools_props , "key_floatmoveunit")

        row = layout.row(align=True)
        row.operator("object.my_operator_gx1", text="GX", icon="COLORSET_01_VEC")
        row.operator("object.my_operator_gy1", text="GY", icon="COLORSET_03_VEC")
        row.operator("object.my_operator_gz1", text="GZ", icon="COLORSET_04_VEC")

#        col = layout.column(align=True)
#        col.prop(wm.super_tools_props , "key_floatmoveunit")
#
        #col.label(text="Exact Move Buttons:")
        #row2 = layout.row()
        colx = layout.column(align=True)
        rowx = layout.row()
        rowx.prop(wm.super_tools_props, "key_floatxg")
        rowx.prop(wm.super_tools_props, "key_floatyg")
        rowx.prop(wm.super_tools_props, "key_floatzg")


        colm = layout.column(align=True)
        rowm = layout.row()
        rowm.operator("object.my_operator_move", text="Move", icon="COLORSET_04_VEC")
        rowm.operator("object.my_operator_resetmove", text="Reset Move Values", icon="COLORSET_04_VEC")

        cole = layout.column(align=True) 
        cole.label(text="Quick Extrude Buttons")       
        rowe = layout.row()
        rowe.operator("object.my_operator_ex1", text="EX1", icon="COLLECTION_COLOR_01")
        rowe.operator("object.my_operator_ey1", text="EY1", icon="COLLECTION_COLOR_04")
        rowe.operator("object.my_operator_ez1", text="EZ1", icon="COLLECTION_COLOR_05")

        colee = layout.column(align=True) 
        colee.label(text="Exact Extrude Buttons")  
        rowee = layout.row()
        rowee.prop(wm.super_tools_props, "key_floatx")
        rowee.prop(wm.super_tools_props, "key_floaty")
        rowee.prop(wm.super_tools_props, "key_floatz")  
        row4b = layout.row()
        row4b.operator("OBJECT_OT_my_operator_exact",text="Extrude using  X,Y,Z",icon="MOD_WIREFRAME")
        row4b.operator("OBJECT_OT_my_operator_reset",text="Reset Extrude Values to 0",icon="PANEL_CLOSE")

        coles = layout.column(align=True) 
        coles.label(text="Scale")  
        rowes = layout.row()
        rowes.prop(wm.super_tools_props, "key_floatxs")
        rowes.prop(wm.super_tools_props, "key_floatys")
        rowes.prop(wm.super_tools_props, "key_floatzs")

        c5b = layout.column(align=True)        
        row5b = layout.row()
        row5b.operator("OBJECT_OT_my_operator_scale",text="Scale",icon="SHADING_BBOX")
        row5b.operator("OBJECT_OT_my_operator_resetscale",text="Reset Scales to 1",icon="LOOP_BACK")
  



        

        scene = context.scene
        #superProps = context.window_manager.super_tools_props
        propfloat = scene.tool_settings.proportional_size
        print('propfloat')
        print(propfloat)

        


    

        
        

#        col = layout.column(align=True)
#        
#        col.label(text="Generation Settings:")
#        col.prop(wm.super_tools_props, "key_floatmoveunit")
#        

        
     


class SuperToolsProperties(PropertyGroup):
    key_median: BoolProperty(
        name="Float Move Unit",
        description="The amount to move the object/mesh",
        default=True,
    )
    key_floatmoveunit: FloatProperty(
        name="Float Move Unit",
        description="The amount to move the object/mesh",
        default=1.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatxg: FloatProperty(
        name="Float Move Unit",
        description="Exact move x",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatyg: FloatProperty(
        name="Float Move Unit",
        description="Exact move y",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatzg: FloatProperty(
        name="Float Move Unit",
        description="Exact move z",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatx: FloatProperty(
        name="Float Move Unit",
        description="Exact extrude x",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floaty: FloatProperty(
        name="Float Move Unit",
        description="Exact extrude y",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatz: FloatProperty(
        name="Float Move Unit",
        description="Exact extrude z",
        default=0.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatxs: FloatProperty(
        name="Float Move Unit",
        description="Scale x",
        default=1.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatys: FloatProperty(
        name="Float Move Unit",
        description="Scale y",
        default=1.000,
        min=-10000.0,
        soft_max=1000.0,
    )

    key_floatzs: FloatProperty(
        name="Float Move Unit",
        description="Scale z",
        default=1.000,
        min=-10000.0,
        soft_max=1000.0,
    )

classes = (
    SuperToolsProperties,
    CURVE_PT_SuperToolsPanel,
    OBJECT_OT_my_operator_gx1,
    OBJECT_OT_my_operator_gy1,
    OBJECT_OT_my_operator_gz1,
    OBJECT_OT_my_operator_emulate,
    OBJECT_OT_my_operator_move,
    OBJECT_OT_my_operator_resetmove,
    OBJECT_OT_my_operator_ex1,
    OBJECT_OT_my_operator_ey1,
    OBJECT_OT_my_operator_ez1,
    OBJECT_OT_my_operator_exact,
    OBJECT_OT_my_operator_reset,
    OBJECT_OT_my_operator_scale,
    OBJECT_OT_my_operator_resetscale
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.super_tools_props = PointerProperty(
        type=SuperToolsProperties
    )


def unregister():
    del bpy.types.WindowManager.super_tools_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()




