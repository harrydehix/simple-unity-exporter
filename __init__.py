bl_info = {
    "name": "Simple Unity Export",
    "author": "Henri Hollmann",
    "version": (0, 0, 3),
    "blender": (4, 3, 2),
    "location": "3D Viewport > Sidebar > Simple Unity export",
    "description": "This addons allows you to simply export blender assets to unity. Support is limited to Principled BSDF. To correctly import any asset you need the 'FixTextureMaps' script located inside your unity project. After that simply drag all export folders to unity.",
    "category": "Unity",
}

if "bpy" in locals():
    import importlib
    importlib.reload(settings)
    importlib.reload(simple_unity_operator)
    importlib.reload(main_panel)
    importlib.reload(properties_panel)
else:
    from . import settings
    from . import simple_unity_operator
    from . import main_panel
    from . import properties_panel

import bpy

classes = (
    simple_unity_operator.SimpleUnityExportOperator, 
    main_panel.MainPanel, main_panel.ApplyPanel, main_panel.MapsPanel, properties_panel.ObjectPropertiesPanel, main_panel.ChildrenPanel
)

def register():
    bpy.utils.register_class(settings.ExportSettings)
    bpy.utils.register_class(settings.ObjectExportSettings)
    bpy.types.Scene.simple_unity_export = bpy.props.PointerProperty(type=settings.ExportSettings)
    bpy.types.Object.simple_unity_export_object = bpy.props.PointerProperty(type=settings.ObjectExportSettings)
    bpy.types.VIEW3D_MT_object.append(lambda self, context: self.layout.operator(simple_unity_operator.SimpleUnityExportOperator.bl_idname, text="Export selected objects to unity"))

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.simple_unity_export
    del bpy.types.Object.simple_unity_export_object
