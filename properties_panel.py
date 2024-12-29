import bpy

class ObjectPropertiesPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Simple Unity Export - Override"
    bl_idname = "OBJECT_PT_simple_unity_export"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Simple Unity Export"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Overrides global export settings", icon='INFO_LARGE')
        row = layout.row()
        
        # Settings
        props = obj.simple_unity_export_object
        if props == None:
            return
        
        (header, body) = layout.panel("Apply")
        header.label(text="Apply")
        if body != None:
            body.prop(props, "override_apply")
            if props.override_apply:
                body.row()
                body.prop(props, "apply_modifiers")
                body.prop(props, "apply_scale")
                body.prop(props, "apply_rotation")
                body.prop(props, "apply_location")
        
        (header, body) = layout.panel("Material")
        header.label(text="Material")
        if body != None:
            body.prop(props, "override_material")
            if props.override_material:
                body.row()
                body.prop(props, "map_width")
                body.prop(props, "map_height")
                body.prop(props, "base_map")
                body.prop(props, "metallic_map")
                body.prop(props, "normal_map")
                #body.prop(props, "height_map")
                #body.prop(props, "occlusion_map")
                body.prop(props, "emission_map")