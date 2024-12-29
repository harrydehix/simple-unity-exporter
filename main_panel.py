import bpy

class MainPanel(bpy.types.Panel):
    """Creates a Panel in the 3D view"""
    bl_label = "Simple Unity Export"
    bl_idname = "VIEW3D_PT_simple_unity_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Simple Unity Export"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Use this addon to export selected objects to unity.", icon='INFO_LARGE')

        row = layout.row()
        
        # Settings
        props = context.scene.simple_unity_export
        
        layout.prop(props, "individual_folder")
        layout.prop(props, "export_base_directory")
        
        row = layout.row()
        layout.operator("object.simple_unity_export_operator")
        if props.progress > 0.0:
            layout.progress(factor = props.progress, type = 'BAR', text = 'Exporting...')
        else:
            layout.label(text = "Select an object to export!")


class ApplyPanel(bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_simple_unity_export"
    bl_label = "Apply"
    bl_idname = "VIEW3D_PT_simple_unity_export_apply"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        props = context.scene.simple_unity_export
        layout.prop(props, "apply_modifiers")
        layout.prop(props, "apply_scale")
        layout.prop(props, "apply_rotation")
        layout.prop(props, "apply_location")
        
class MapsPanel(bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_simple_unity_export"
    bl_label = "Material"
    bl_idname = "VIEW3D_PT_simple_unity_export_maps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        props = context.scene.simple_unity_export
        row = layout.row()
        row.label(text="Only supports Principled BSDF", icon="ERROR")
        layout.prop(props, "map_width")
        layout.prop(props, "map_height")
        layout.prop(props, "base_map")
        layout.prop(props, "metallic_map")
        layout.prop(props, "normal_map")
        #layout.prop(props, "height_map")
        #layout.prop(props, "occlusion_map")
        layout.prop(props, "emission_map")
        
class ChildrenPanel(bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_simple_unity_export"
    bl_label = "Children"
    bl_idname = "VIEW3D_PT_simple_unity_export_children"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        props = context.scene.simple_unity_export
        row = layout.row()
        layout.prop(props, "children")



