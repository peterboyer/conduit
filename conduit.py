import bpy

bl_info = {
    "name": "Conduit",
    "blender": (3, 6, 0),
    "category": "Import-Export"
}


def xyz(value):
    return (value.x, value.y, value.z)


class ExportOperator(bpy.types.Operator):
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
            # Custom Properties.
            export_extras=True,
        )

        return {'FINISHED'}


class ExportPanel(bpy.types.Panel):
    bl_idname = "CONDUIT_PT_panel"
    bl_label = "Conduit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conduit"

    def draw(self, context):
        self.layout.operator(ExportOperator.bl_idname, text=ExportOperator.bl_label)


class ObjectPropertiesPanel(bpy.types.Panel):
    bl_idname = "CONDUIT_PT_object_panel"
    bl_label = "Conduit"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        self.layout.prop(
            context.active_object,
            "conduit_placeholder",
            text="Placeholder"
        )


def menu_func_export(self, context):
    self.layout.operator(ExportOperator.bl_idname, text=ExportOperator.bl_label)


#  @bpy.app.handlers.persistent
#  def obj_init(scene):
#      if hasattr(bpy.context, "object") and bpy.context.object.placeholder is not None:
#          print("obj:init", scene)
#          bpy.context.object.placeholder = None


# https://b3d.interplanety.org/en/creating-panels-for-placing-blender-add-ons-user-interface-ui/
# https://s-nako.work/2020/12/how-to-add-properties-in-your-blender-addon-ui/
# https://s-nako.work/2020/12/how-to-display-custom-property-on-properties-editor-in-blender-addon/

def register():
    print("mount")
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(ExportPanel)

    bpy.types.Object.conduit_placeholder = bpy.props.PointerProperty(
        name="ConduitPlaceholder", type=bpy.types.Object)
    #  bpy.app.handlers.depsgraph_update_post.append(obj_init)

    bpy.utils.register_class(ObjectPropertiesPanel)

    print("mount:done")


def unregister():
    print("unmount")
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ExportPanel)

    del bpy.types.Object.conduit_placeholder
    #  bpy.app.handlers.depsgraph_update_post.remove(obj_init)

    bpy.utils.unregister_class(ObjectPropertiesPanel)

    print("unmount:done")
