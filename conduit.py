import bpy

bl_info = {
	"name": "Conduit",
	"blender": (3, 6, 0),
	"category": "Import-Export"
}


class ExportOperator(bpy.types.Operator):
	bl_idname = "conduit.export"
	bl_label = "Export scene.gltf"
	bl_options = {'REGISTER'}

	def execute(self, ctx):
		if not bpy.data.is_saved:
			self.report({'WARNING'}, "Scene must be saved first.")
			return {'CANCELLED'}

		# (object, conduit_placeholder,)[]
		restore_placeholders = []

		for object in bpy.data.objects:
			value = object.conduit_placeholder
			if value is not None:
				object.instance_type = 'NONE'
				object.instance_collection = None
				restore_placeholders.append({object, value})

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

		for restore_placeholder in restore_placeholders:
			object, value = restore_placeholder
			object.instance_type = 'COLLECTION'
			object.instance_collection = value

		return {'FINISHED'}


class ExportPanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_panel"
	bl_label = "Conduit"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Conduit"

	def draw(self, ctx):
		self.layout.operator(
			ExportOperator.bl_idname,
			text=ExportOperator.bl_label,
		)


class ObjectPropertiesPanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_object_panel"
	bl_label = "Conduit"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	@classmethod
	def poll(cls, ctx):
		return (ctx.object.type in {'EMPTY'})

	def draw(self, ctx):
		self.layout.prop(
			ctx.object,
			"conduit_placeholder",
			text="Placeholder",
		)


def on_placeholder_update(self, ctx):
	value = self.conduit_placeholder
	if value is None:
		self.instance_type = 'NONE'
		self.instance_collection = None
	else:
		self.instance_type = 'COLLECTION'
		self.instance_collection = value


class SceneActorItemProperty(bpy.types.PropertyGroup):
	pass


class SceneActorAddOperator(bpy.types.Operator):
	bl_idname = "conduit.scene_actors_add"
	bl_label = "Add a new actor type"

	def execute(self, ctx):
		ctx.scene.conduit_actors.add()
		return {'FINISHED'}


class SceneActorRemoveOperator(bpy.types.Operator):
	bl_idname = "conduit.scene_actors_remove"
	bl_label = "Remove an existing actor type"

	def execute(self, ctx):
		ctx.scene.conduit_actors.remove(ctx.scene.conduit_actors_active_index)
		return {'FINISHED'}


class ScenePropertiesPanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_scene_panel"
	bl_label = "Conduit"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, ctx):
		row = self.layout.row()

		template_list_options = {
			"list_type": "UI_UL_list",
			"list_id": "conduit_actors",
			"data": (ctx.scene, "conduit_actors"),
			"data_active_index": (ctx.scene, "conduit_actors_active_index"),
		}

		col = row.column()
		col.template_list(
			template_list_options["list_type"],
			template_list_options["list_id"],
			template_list_options["data"][0],
			template_list_options["data"][1],
			template_list_options["data_active_index"][0],
			template_list_options["data_active_index"][1],
			rows=4
		)

		col = row.column(align=True)
		col.operator(SceneActorAddOperator.bl_idname, icon='ADD', text="")
		col.operator(SceneActorRemoveOperator.bl_idname, icon='REMOVE', text="")


# https://b3d.interplanety.org/en/creating-panels-for-placing-blender-add-ons-user-interface-ui/
# https://s-nako.work/2020/12/how-to-add-properties-in-your-blender-addon-ui/
# https://s-nako.work/2020/12/how-to-display-custom-property-on-properties-editor-in-blender-addon/
# https://en.wikibooks.org/wiki/Blender_3D%3A_Noob_to_Pro/Advanced_Tutorials/Python_Scripting/Addon_Custom_Property

def register():
	# types
	bpy.utils.register_class(SceneActorItemProperty)

	# props
	bpy.types.Scene.conduit_actors = \
		bpy.props.CollectionProperty(
			type=SceneActorItemProperty,
		)
	bpy.types.Scene.conduit_actors_active_index = \
		bpy.props.IntProperty(
			default=0
		)
	bpy.types.Object.conduit_placeholder = \
		bpy.props.PointerProperty(
			type=bpy.types.Collection,
			update=on_placeholder_update,
		)

	# actions
	bpy.utils.register_class(ExportOperator)
	bpy.utils.register_class(SceneActorAddOperator)
	bpy.utils.register_class(SceneActorRemoveOperator)

	# panels
	bpy.utils.register_class(ScenePropertiesPanel)
	bpy.utils.register_class(ObjectPropertiesPanel)
	bpy.utils.register_class(ExportPanel)


def unregister():
	# panels
	bpy.utils.unregister_class(ScenePropertiesPanel)
	bpy.utils.unregister_class(ObjectPropertiesPanel)
	bpy.utils.unregister_class(ExportPanel)

	# actions
	bpy.utils.unregister_class(ExportOperator)

	# props
	del bpy.types.Scene.conduit_actors
	del bpy.types.Object.conduit_placeholder

	# types
	bpy.utils.unregister_class(SceneActorItemProperty)
