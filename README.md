# simple-unity-exporter

Simple addon to export *meshes*, *curves* and *texts* from blender to unity without having to manually apply modifiers, apply transforms and bake textures.

<img src="./screenshots/image.png" height=400>
<img src="./screenshots/image1.png" width=400>

_Tested with Blender 4.3.2 and Unity 6_

⚠️ I developed this addon for personal uses. There might be some issues. If you encounter a bug please create an issue.

## How to use this addon
1. Drag the "FixTextureMaps.cs" file into your unity asset folder (only once)
2. Select the objects you want to export
3. Open the addon inside the 3D View using "N"
3. Choose an export folder (not inside your unity asset folder)
4. Click export
5. Drag the whole export folder into your unity project
6. If an popup with "Fix now" appears, click "Fix now"

## Export Settings
The export settings you define inside the 3D View are used for all objects inside the same scene. If you want to change the export settings for particular objects go to `Object Properties > Simple Unity Export - Override`.

### Apply
In this section you configure if modifiers, scale, rotation and location are applied before exporting. Your original model is untouched - no worries!

### Material
In this section you configure how materials are exported. The individual maps correspond to the Principled BSDF shader settings. 

The texture width and height define the resolution. It is recommended to stay in an area between 512 and 2048. Higher values might crash blender.

### Children
In this section you configure how children of selected objects are treated. If you select "Include in parent .fbx file" or "Export in seperated .fbx file" don't select them on exporting. Otherwise you will export them twice.

## Limitations for materials
Only works partly with Principled BSDF. The following shader settings are supported:
- BSDF Normal Map Input (any node input, gets baked)
- BSDF Base Color Input (any node input, gets baked)
- BSDF Roughness Value (only a fixed value)
- BSDF Metallic Input (any node input, gets baked)
- BSDF Emission Color Input (any node input, gets baked)
- BSDF Emission Strength Value (only a fixed value)

## Limitations for UV Maps
This addon automatically unwraps your models using the Smart UV Project. Because of that your nodes should only work with "Generated" Texture Coordinates and not custom UV maps. 

If wanted I can add another option to use the existing UV Map (just create an issue :D).