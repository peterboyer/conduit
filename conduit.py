import bpy

bl_info = {
    "name": "Conduit",
    "blender": (2, 80, 0),
    "category": "Import-Export"
}


def xyz(value):
    return (value.x, value.y, value.z)


class ExportScene(bpy.types.Operator):
    bl_idname = "conduit.export"
    bl_label = "Export scene.gltf"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'WARNING'}, "Scene must be saved first.")
            return {'CANCELLED'}

        filepath = bpy.path.abspath("//") + "scene.gltf"

        # https://docs.blender.org/api/current/bpy.ops.export_scene.html
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            check_existing=False,
            # Unitless, works best for Three.
            export_import_convert_lighting_mode="COMPAT",
            # Single file.
            export_format="GLTF_EMBEDDED",
            # Cameras.
            export_cameras=True,
            # Lights.
            export_lights=True,
        )

        return {'FINISHED'}


class Panel(bpy.types.Panel):
    bl_idname = "CONDUIT_PT_panel"
    bl_label = "Conduit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conduit"

    def draw(self, context):
        self.layout.operator(ExportScene.bl_idname, text=ExportScene.bl_label)


def menu_func_export(self, context):
    self.layout.operator(ExportScene.bl_idname, text=ExportScene.bl_label)


def register():
    print("register")
    bpy.utils.register_class(ExportScene)
    bpy.utils.register_class(Panel)


def unregister():
    print("unregister")
    bpy.utils.unregister_class(ExportScene)
    bpy.utils.unregister_class(Panel)
