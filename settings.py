import bpy

class ExportSettings(bpy.types.PropertyGroup):
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply modifiers",
        description="Apply all modifiers before exporting",
        default=True
    )
    
    apply_rotation: bpy.props.BoolProperty(
        name="Apply rotation",
        description="Apply rotation before exporting",
        default=True
    )
    
    apply_scale: bpy.props.BoolProperty(
        name="Apply scale",
        description="Apply scale before exporting",
        default=True
    )
    
    apply_location: bpy.props.BoolProperty(
        name="Apply location",
        description="Apply location before exporting",
        default=False
    )

    individual_folder: bpy.props.BoolProperty(
        name="Individual export folders",
        description="Create an individual folder for each exported object",
        default=False
    )
    
    export_base_directory: bpy.props.StringProperty(
        name="Base export directory",
        description="All .fbx files are exported to this directory",
        default="//",
        subtype='DIR_PATH'
    )
    
    map_width: bpy.props.IntProperty(
        name="Texture Width",
        description="Any map's width",
        default=1024,
        min=0
    )
    
    map_height: bpy.props.IntProperty(
        name="Texture Height",
        description="Any map's height",
        default=1024,
        min=0
    )
    
    base_map: bpy.props.BoolProperty(
        name="Base Map",
        description="Generate Base Map from BSDF Base color input",
        default=True
    )
    
    metallic_map: bpy.props.BoolProperty(
        name="Metallic Map",
        description="Generate Metallic Map from BSDF Metallic input",
        default=True
    )
    
    normal_map: bpy.props.BoolProperty(
        name="Normal Map",
        description="Generate Normal Map from BSDF Normal input",
        default=True
    )
    
    height_map: bpy.props.BoolProperty(
        name="Height Map",
        description="Generate Height Map from Displacement input",
        default=False
    )
    
    occlusion_map: bpy.props.BoolProperty(
        name="Occlusion Map",
        description="Generate Occlusion Map from Scene Lighting",
        default=False
    )
    
    emission_map: bpy.props.BoolProperty(
        name="Emission Map",
        description="Generate Emission Map from BSDF Emission color and strength input",
        default=False
    )
    
    children: bpy.props.EnumProperty(
        name='',
        items=(
            ('include', "Include in parent .fbx file (recommended)", ""),
            ('seperate', "Export in separated .fbx file", ""),
            ('ignore', "Do not export", "")
        )
    )
    
    progress: bpy.props.FloatProperty(
        name="Progress",
        default=-1
    )
    
class ObjectExportSettings(ExportSettings):
    override_material: bpy.props.BoolProperty(
        name="Override material settings",
        description="Ignore global material export settings and use the settings defined in this property window",
        default=False
    )
    
    override_apply: bpy.props.BoolProperty(
        name="Override apply settings",
        description="Ignore global apply export settings and use the settings defined in this property window",
        default=False
    )
