import bpy
import os

class SimpleUnityExportOperator(bpy.types.Operator):
    """Exports selected objects"""
    bl_idname = "object.simple_unity_export_operator"
    bl_label = "Export"
    bl_category = "Simple Unity Export"
    
    def delete_and_clear_object(self, object):
        for mat_slot in object.material_slots:
            if mat_slot.material:
                bpy.data.materials.remove(mat_slot.material, do_unlink=True)
                
        object_data = object.data
        bpy.data.objects.remove(object, do_unlink=True)
        bpy.data.meshes.remove(object_data)
    
    def select_object(self, object):
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
    
    def copy_materials(self, object):
        for i, slot in enumerate(object.material_slots):
            new_material = slot.material.copy()
            object.material_slots[i].material = new_material
    
    def create_texture(self, path, width, height, name):
        texture = bpy.data.images.new(name=name, width=width, height=height)
        file_path = os.path.join(path, f"{name}.png")
        texture.filepath_raw = file_path
        texture.file_format = 'PNG'
        return texture
    
    def add_node_for_texture(self, material, texture):
        nodes = material.node_tree.nodes
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.location = (0, 0)
        texture_node.image = texture
        return texture_node
                
    def get_texture_node(self, material, texture):
        nodes = material.node_tree.nodes
        texture_node = None
        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage) and node.image == texture:
                texture_node = node
        return texture_node
    
    def get_principled_node(self, material):
        nodes = material.node_tree.nodes
        principled_node = None
        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
                principled_node = node
        return principled_node
    
    def select_node(self, material, node):
        nodes = material.node_tree.nodes
        for n in nodes:
            n.select = False
        node.select = True
        nodes.active = node
        return node
    
    def save_image(self, image):
        image.save()
        
    def override_object_props(self, global_props, object):
        object_props = object.simple_unity_export_object

        object_props.individual_folder = global_props.individual_folder
        object_props.export_base_directory = global_props.export_base_directory
        object_props.children = global_props.children

        if not object_props.override_apply:
            object_props.apply_scale = global_props.apply_scale
            object_props.apply_rotation = global_props.apply_rotation
            object_props.apply_modifiers = global_props.apply_modifiers
            object_props.apply_location = global_props.apply_location

        if not object_props.override_material:
            object_props.map_width = global_props.map_width
            object_props.map_height = global_props.map_height
            object_props.base_map = global_props.base_map
            object_props.metallic_map = global_props.metallic_map
            object_props.normal_map = global_props.normal_map
            object_props.height_map = global_props.height_map
            object_props.occlusion_map = global_props.occlusion_map
            object_props.emission_map = global_props.emission_map

        return object_props
                
    def bake_bsdf_input_to_texture(self, object_name, object, bsdf_input_name, texture_suffix, width, height, export_folder):
        # Create texture
        self.report({'INFO'}, f"Baking texture '{object_name}_{texture_suffix}'")
        texture = self.create_texture(path=export_folder, width=width, height=height, name=f"{object_name}_{texture_suffix}")
        
        original_base_color_input_sockets = {}
        original_roughnesses = {}
        original_metallics = {}
        original_roughness_sockets = {}
        original_metallic_sockets = {}
        should_be_ignored = {}
        baking_is_needed = False
        
        for i, slot in enumerate(object.material_slots):
            material = slot.material
            if material is not None and material.use_nodes:
                node_tree = material.node_tree
                
                # Get principled node
                principled_node = self.get_principled_node(material)
                
                if not principled_node or not principled_node.inputs[bsdf_input_name].is_linked:
                    # Skip materials without any principled node or any map input
                    self.report({'INFO'}, f"Ignoring material '{material.name}' because there is no relevant input")
                    should_be_ignored[i] = True
                    continue
                else:
                    baking_is_needed = True
                    should_be_ignored[i] = False
                
                # Add texture node to each material slot
                texture_node = self.add_node_for_texture(material, texture)
                
                # Temporary link bsdf input to base color input
                if bsdf_input_name != "Normal" and bsdf_input_name != "Base Color":
                    original_base_color_link = principled_node.inputs["Base Color"].links[0]
                    original_base_color_input_sockets[i] = original_base_color_link.from_socket
                    node_tree.links.remove(original_base_color_link)
                    
                    # Plug input to base color (if not normal/base map)
                    socket = principled_node.inputs[bsdf_input_name].links[0].from_socket
                    node_tree.links.new(socket, principled_node.inputs["Base Color"])
                    
                original_roughness_link = principled_node.inputs['Roughness'].links[0] if principled_node.inputs['Roughness'].is_linked else None
                original_roughness_sockets[i] = principled_node.inputs['Roughness'].links[0].from_socket if principled_node.inputs['Roughness'].is_linked else None
                original_roughnesses[i] = principled_node.inputs['Roughness'].default_value
                original_metallic_link = principled_node.inputs['Metallic'].links[0] if principled_node.inputs['Metallic'].is_linked else None
                original_metallic_sockets[i] = principled_node.inputs['Metallic'].links[0].from_socket if principled_node.inputs['Metallic'].is_linked else None
                original_metallics[i] = principled_node.inputs['Metallic'].default_value
                
                # Set roughness and metallic (for base color export)
                if bsdf_input_name != "Normal":
                    principled_node.inputs['Metallic'].default_value = 0.0
                    if principled_node.inputs['Metallic'].is_linked:
                        node_tree.links.remove(original_metallic_link)
                    principled_node.inputs['Roughness'].default_value = 1.0
                    if principled_node.inputs['Roughness'].is_linked:
                        node_tree.links.remove(original_roughness_link)
                
                if bsdf_input_name != "Base Color":
                    # Set normal node color type to "Non Color"
                    texture_node.image.colorspace_settings.name = 'Non-Color'
                    
                # Select texture node
                self.select_node(material, texture_node)
        
        # Return if no baking is needed
        if not baking_is_needed:
            self.report({'INFO'}, f"No '{bsdf_input_name}' input found, not generating any texture!")
            return (True, texture) 
        
        # Bake base color input (or normal input) to texture
        samples_before = bpy.context.scene.cycles.samples
        bpy.context.scene.cycles.samples = 1
        if bsdf_input_name != "Normal":
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.bake_type = 'DIFFUSE'
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
        else:
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.bake_type = 'NORMAL'
            bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
        self.save_image(texture)
        bpy.context.scene.cycles.samples = samples_before
        
        # Change node links 
        for i, slot in enumerate(object.material_slots):
            material = slot.material
            node_tree = slot.material.node_tree
            
            # Get principled node
            principled_node = self.get_principled_node(material)

            self.report({'INFO'}, f"Setting baked texture of material '{material.name}'")
            if should_be_ignored[i]:
                # Skip materials without any principled node or any map input
                self.report({'INFO'}, f"Ignoring material '{material.name}' because there is no relevant input")
                continue
            
            # Get texture node
            texture_node = self.get_texture_node(material, texture)
            
            # Restore original base color input (if not normal / base)
            original_link = None
            if bsdf_input_name != "Normal" and bsdf_input_name != "Base Color":
                original_link = node_tree.links.new(original_base_color_input_sockets[i], principled_node.inputs["Base Color"])
            
            # Reset roughness and metallic
            if bsdf_input_name != "Normal":
                if bsdf_input_name != "Metallic":
                    principled_node.inputs['Metallic'].default_value = original_metallics[i]
                    if original_metallic_sockets[i] != None:
                        node_tree.links.new(original_metallic_sockets[i], principled_node.inputs["Metallic"])
                if bsdf_input_name != "Roughness":
                    principled_node.inputs['Roughness'].default_value = original_roughnesses[i]
                    if original_roughness_sockets[i] != None:
                        node_tree.links.new(original_roughness_sockets[i], principled_node.inputs["Roughness"])
            
            # Link baked texture to desired input
            if bsdf_input_name != "Normal":
                node_tree.links.new(texture_node.outputs["Color"], principled_node.inputs[bsdf_input_name])
            else:
                normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
                node_tree.links.new(texture_node.outputs['Color'], normal_map_node.inputs['Color']) # Add normal map node if normals are baked
                node_tree.links.new(normal_map_node.outputs['Normal'], principled_node.inputs['Normal'])   
    
        return (True, texture)
    
    def start_progress(self, props):
        props.progress = 0
        self.redraw_tools_window()

    def redraw_tools_window(self):
        area_3d = None
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                area_3d = area
        if area_3d != None:
            for region in area_3d.regions:
                if(region.type == "TOOLS"):
                    region.tag_redraw()
        
    def update_progress(self, props, value):
        props.progress = value
        self.redraw_tools_window()

    def end_progress(self, props):
        props.progress = -1
        self.redraw_tools_window()
        
    def create_baked_duplicate(self, context, object_props, scene_props, obj, progress_step, export_folder):
        # Duplicate object
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        self.copy_materials(new_obj)

        # Add duplicate to scene
        bpy.context.collection.objects.link(new_obj)

        # Set duplicate as active object
        bpy.context.view_layer.objects.active = new_obj

        self.report({'INFO'}, f"Duplicated '{obj.name}'!")
        
        # Only select duplicate
        self.select_object(new_obj)

        # Convert to mesh if curve or text 
        if new_obj.type == 'CURVE' or new_obj.type == 'FONT':
            bpy.ops.object.convert(target='MESH')
            self.report({'INFO'}, f"Converted '{obj.name}' to mesh!")

        # Apply modifiers to duplicate
        if object_props.apply_modifiers:
            for modifier in new_obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                
        self.update_progress(scene_props, scene_props.progress + progress_step * 0.1)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                
        # Apply transforms to duplicate
        bpy.ops.object.transform_apply(location=object_props.apply_location, scale=object_props.apply_scale, rotation=object_props.apply_rotation)
        
        # Select duplicate
        self.select_object(new_obj)
        
        # UV unwrap (add uv map if not existing)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        uv_layers = new_obj.data.uv_layers
        uv_map = uv_layers.active
        if uv_map is None:
            uv_map = uv_layers.new(name="UVMap")
        uv_map.active_render = True
        uv_layers.active = uv_map
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Select duplicate
        self.select_object(new_obj)
        
        # Bake textures
        textures = []
        # Base color map
        if object_props.base_map:
            (success, texture) = self.bake_bsdf_input_to_texture(
                object_name = obj.name, 
                object = new_obj, 
                bsdf_input_name = "Base Color", 
                texture_suffix = "BaseColor", 
                width = object_props.map_width, 
                height = object_props.map_height, 
                export_folder = export_folder
            )
            if texture != None:
                textures.append(texture)
            if not success:
                return (False, textures, None)
        self.update_progress(scene_props, scene_props.progress + progress_step * 0.2)
        
        # Metallic map
        if object_props.metallic_map:
            (success, texture) = self.bake_bsdf_input_to_texture(
                object_name = obj.name, 
                object = new_obj, 
                bsdf_input_name = "Metallic", 
                texture_suffix = "MetallicGlossMap", 
                width = object_props.map_width, 
                height = object_props.map_height, 
                export_folder = export_folder
            )
            if texture != None:
                textures.append(texture)
            if not success:
                return (False, textures, None)
        self.update_progress(scene_props, scene_props.progress + progress_step * 0.2)
        
        # Normal map
        if object_props.normal_map:
            (success, texture) = self.bake_bsdf_input_to_texture(
                object_name = obj.name, 
                object = new_obj, 
                bsdf_input_name = "Normal", 
                texture_suffix = "Normal", 
                width = object_props.map_width, 
                height = object_props.map_height, 
                export_folder = export_folder
            )
            if texture != None:
                textures.append(texture)
            if not success:
                return (False, textures, None)
        self.update_progress(scene_props, scene_props.progress + progress_step * 0.2)
            
        # Emission map
        if object_props.emission_map:
            (success, texture) = self.bake_bsdf_input_to_texture(
                object_name = obj.name, 
                object = new_obj, 
                bsdf_input_name = "Emission Color", 
                texture_suffix = "Emission", 
                width = object_props.map_width, 
                height = object_props.map_height, 
                export_folder = export_folder
            )
            if texture != None:
                textures.append(texture)
            if not success:
                return (False, textures, None)
        self.update_progress(scene_props, scene_props.progress + progress_step * 0.2)
        return (True, textures, new_obj)
    
    def delete_texture(self, texture_name):
        texture = bpy.data.images.get(texture_name)
        if not texture:
            self.report({'INFO'}, f"Didn't delete texture - does not exist!")
            return False

        if texture.users > 0:
            self.report({'INFO'}, f"Didn't delete texture - still referenced!")
            return False
        
        bpy.data.images.remove(texture)
        self.report({'INFO'}, f"Deleted texture: {texture_name}")
        return True
        
    def export_active_object(self, context, progress_step):
        scene_props = context.scene.simple_unity_export
        
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Reference to original object
        obj = context.active_object
        
        if len(obj.material_slots) == 0:
            self.report({'ERROR'}, f"Cannot export an object '{obj.name}' without any material!")
            return False
        
        # Create / Set export folder
        export_folder = scene_props.export_base_directory
        if scene_props.individual_folder:
            export_folder = os.path.join(export_folder, obj.name)
            if not os.path.exists(export_folder):
                os.makedirs(export_folder)
                
        # objects to duplicate and bake
        objects = [obj]
        new_objects = []
        
        # Children       
        obj_children = obj.children_recursive
        if len(obj_children) != 0 and scene_props.children == "include":
            self.report({'INFO'}, f"Including children!")
            objects.extend(obj_children)
        
        # Duplicate and bake object
        textures = []
        for current_obj in objects:
            object_props = self.override_object_props(scene_props, current_obj)
            (success, new_textures, new_obj) = self.create_baked_duplicate(context, object_props, scene_props, current_obj, progress_step / len(objects), export_folder)
            if success:
                new_objects.append(new_obj)
            else:
                self.report({'WARN'}, f"Failed to create baked duplicate of '{current_obj.name}'")
            textures.extend(new_textures)
            
        export_file = os.path.join(export_folder, obj.name + ".fbx")
            
        # Select all objects to export
        bpy.ops.object.select_all(action='DESELECT')
        for current_obj in new_objects:
            current_obj.select_set(True)
            
        # Export
        bpy.ops.export_scene.fbx(filepath=export_file, use_selection=True, axis_up='Y', axis_forward='-Z')
        
        # Delete duplicate, materials, etc
        # Delete object
        for current_obj in new_objects:
            self.delete_and_clear_object(current_obj)

        # Only select original
        self.select_object(obj)

        # Delete textures from blend file
        for texture in textures:
            self.report({'INFO'}, f"Texture to delete: {texture.name}")
            self.delete_texture(texture.name)

        return True
    
    def execute(self, context):
        scene_props = context.scene.simple_unity_export

        # Set progress to 0
        self.start_progress(scene_props)
        self.report({'INFO'}, f"Exporting objects...")
        
        obj = context.active_object
        if obj is None or (obj.type != 'MESH' and obj.type != 'CURVE' and obj.type != 'FONT') or not obj.select_get():
            self.report({'ERROR'}, f"Select at least one object (mesh / curve) to export!")
            self.end_progress(scene_props)
            return {'FINISHED'}
        
        selected_objects_reset = bpy.context.selected_objects
        selected_objects = bpy.context.selected_objects
        progress_step = 1 / len(selected_objects)
        for obj in selected_objects:
                    
            obj_children = obj.children_recursive
            if len(obj_children) != 0:
                self.report({'INFO'}, f"Detected children!")
                # Handle children
                if scene_props.children == "seperate":
                    # Append children to selected_objects list
                    self.report({'INFO'}, f"Appending children")
                    selected_objects.extend(obj_children)
                    # TODO: Fix progress bar!
            
            self.select_object(obj)
            success = self.export_active_object(context, progress_step) 
            if not success:
                self.end_progress(scene_props)
                return {'FINISHED'}
        
        # Reset selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects_reset:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        self.end_progress(scene_props)
        self.report({'INFO'}, f"Successfully exported objects!")
        return {'FINISHED'}