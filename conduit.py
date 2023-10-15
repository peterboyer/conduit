# https://b3d.interplanety.org/en/creating-panels-for-placing-blender-add-ons-user-interface-ui/
# https://s-nako.work/2020/12/how-to-add-properties-in-your-blender-addon-ui/
# https://s-nako.work/2020/12/how-to-display-custom-property-on-properties-editor-in-blender-addon/
# https://en.wikibooks.org/wiki/Blender_3D%3A_Noob_to_Pro/Advanced_Tutorials/Python_Scripting/Addon_Custom_Property
# https://sinestesia.co/blog/tutorials/using-uilists-in-blender/

import bpy

bl_info = {
	"name": "Conduit",
	"blender": (3, 6, 0),
	"category": "Import-Export"
}


ACTOR_NONE = "__NONE__"


def object_update_placeholder(self, ctx):
	value = self.conduit_actor
	collection = None

	if ctx.scene.conduit_actors:
		for actor in ctx.scene.conduit_actors:
			if (actor.name == value):
				collection = actor.placeholder

	if collection:
		self.instance_type = 'COLLECTION'
		self.instance_collection = collection
		return

	self.instance_type = 'NONE'
	self.instance_collection = None


class ExportOperator(bpy.types.Operator):
	bl_idname = "conduit.export"
	bl_label = "Export scene.gltf"
	bl_options = {'REGISTER'}

	def execute(self, ctx):
		if not bpy.data.is_saved:
			self.report({'WARNING'}, "Scene must be saved first.")
			return {'CANCELLED'}

		# Clear all instance/instance_collection for export, then restore.
		actors = []

		for object in bpy.data.objects:
			actor_id = object.conduit_actor
			if actor_id and actor_id != ACTOR_NONE:
				actors.append((
					object, object.conduit_actor, object.instance_collection))
				object.instance_type = 'NONE'
				object.instance_collection = None

		# Workaround to export literal value instead of enum integer.
		conduit_actor = bpy.types.Object.conduit_actor
		bpy.types.Object.conduit_actor = bpy.props.StringProperty()
		for object, actor_id, instance_collection in actors:
			object.conduit_actor = actor_id

		# https://docs.blender.org/api/current/bpy.ops.export_scene.html
		filepath = bpy.path.abspath("//") + "scene.gltf"
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

		# Enum workaround, reset.
		bpy.types.Object.conduit_actor = conduit_actor

		for object, actor_id, instance_collection in actors:
			object.instance_type = 'COLLECTION'
			if not instance_collection:
				object_update_placeholder(object, ctx)
			object.instance_collection = instance_collection
			object.conduit_actor = actor_id

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
			"conduit_actor",
			text="Actor",
		)


def scene_actor_placeholder_update(self, ctx):
	for object in ctx.scene.objects:
		object_update_placeholder(object, ctx)


class SceneActorProperty(bpy.types.PropertyGroup):
	placeholder: bpy.props.PointerProperty(
		type=bpy.types.Collection,
		update=scene_actor_placeholder_update)


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


class CONDUIT_UL_SceneActorsList(bpy.types.UIList):
	def draw_item(self, ctx, layout, data, item, icon, active_data, active_property):
		layout.prop(item, "name", text="", icon="EMPTY_AXIS")
		if item.placeholder:
			layout.label(text=item.placeholder.name, icon='META_CUBE')


class ScenePropertiesPanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_scene_panel"
	bl_label = "Conduit"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, ctx):
		row = self.layout.row()

		template_list_options = {
			"list_type": "CONDUIT_UL_SceneActorsList",
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
			rows=4,
		)

		col = row.column(align=True)
		col.operator(SceneActorAddOperator.bl_idname, icon='ADD', text="")
		col.operator(SceneActorRemoveOperator.bl_idname, icon='REMOVE', text="")

		if ctx.scene.conduit_actors and ctx.scene.conduit_actors_active_index >= 0:
			item = ctx.scene.conduit_actors[ctx.scene.conduit_actors_active_index]
			row = self.layout.row()
			row.prop(item, "placeholder")


def object_actor_items(self, ctx):
	if not ctx:
		return []

	items = [(ACTOR_NONE, 'None', '')]
	for actor in ctx.scene.conduit_actors:
		name = actor.name
		items.append((name, name, ''))
	return items


def object_actor_update(self, ctx):
	object_update_placeholder(self, ctx)


def register():
	# types
	bpy.utils.register_class(SceneActorProperty)

	# props
	bpy.types.Scene.conduit_actors = \
		bpy.props.CollectionProperty(type=SceneActorProperty)
	bpy.types.Scene.conduit_actors_active_index = \
		bpy.props.IntProperty(default=0)
	bpy.types.Object.conduit_actor = \
		bpy.props.EnumProperty(items=object_actor_items, update=object_actor_update)

	# actions
	bpy.utils.register_class(ExportOperator)
	bpy.utils.register_class(SceneActorAddOperator)
	bpy.utils.register_class(SceneActorRemoveOperator)

	# ui
	bpy.utils.register_class(CONDUIT_UL_SceneActorsList)

	# panels
	bpy.utils.register_class(ScenePropertiesPanel)
	bpy.utils.register_class(ObjectPropertiesPanel)
	bpy.utils.register_class(ExportPanel)


def unregister():
	# panels
	bpy.utils.unregister_class(ScenePropertiesPanel)
	bpy.utils.unregister_class(ObjectPropertiesPanel)
	bpy.utils.unregister_class(ExportPanel)

	# ui
	bpy.utils.unregister_class(CONDUIT_UL_SceneActorsList)

	# actions
	bpy.utils.unregister_class(ExportOperator)
	bpy.utils.unregister_class(SceneActorAddOperator)
	bpy.utils.unregister_class(SceneActorRemoveOperator)

	# props
	del bpy.types.Scene.conduit_actors
	del bpy.types.Object.conduit_actor

	# types
	bpy.utils.unregister_class(SceneActorProperty)
