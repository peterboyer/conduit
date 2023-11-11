# https://b3d.interplanety.org/en/creating-panels-for-placing-blender-add-ons-user-interface-ui/
# https://s-nako.work/2020/12/how-to-add-properties-in-your-blender-addon-ui/
# https://s-nako.work/2020/12/how-to-display-custom-property-on-properties-editor-in-blender-addon/
# https://en.wikibooks.org/wiki/Blender_3D%3A_Noob_to_Pro/Advanced_Tutorials/Python_Scripting/Addon_Custom_Property
# https://sinestesia.co/blog/tutorials/using-uilists-in-blender/

import os
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

	if ctx.workspace.conduit_actors:
		for actor in ctx.workspace.conduit_actors:
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
	bl_label = "Export scene.glb"
	bl_options = {'REGISTER'}

	def execute(self, ctx):
		if not bpy.data.is_saved:
			self.report({'WARNING'}, "Scene must be saved first.")
			return {'CANCELLED'}

		# Clear all instance/instance_collection for export, then restore.
		actors = []
		for object in ctx.scene.objects:
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

		filedir = bpy.path.abspath(ctx.workspace.conduit_export_path or "//")
		filename = ctx.scene.name + ".glb"
		filepath = os.path.abspath(filedir + filename)

		# https://docs.blender.org/api/current/bpy.ops.export_scene.html
		bpy.ops.export_scene.gltf(
			filepath=filepath,
			check_existing=False,
			# Only current scene.
			use_active_scene=True,
			# Unitless, works best for Three.
			export_import_convert_lighting_mode="COMPAT",
			# Single file.
			export_format="GLB",
			# Cameras.
			export_cameras=True,
			# Lights.
			export_lights=True,
			# Custom Properties.
			export_extras=True,
		)

		# Enum workaround, reset.
		bpy.types.Object.conduit_actor = conduit_actor

		# Restore actors properties.
		for object, actor_id, instance_collection in actors:
			object.instance_type = 'COLLECTION'
			if not instance_collection:
				object_update_placeholder(object, ctx)
			object.instance_collection = instance_collection
			object.conduit_actor = actor_id

		return {'FINISHED'}


class WorkspacePanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_panel"
	bl_label = "Conduit"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Conduit"

	def draw(self, ctx):
		filename = ctx.scene.name + ".glb"
		self.layout.operator(
			ExportOperator.bl_idname,
			text="Export as " + filename,
		)
		self.layout.prop(
			ctx.workspace,
			"conduit_export_path",
			text="Path",
		)

		row = self.layout.row()

		template_list_options = {
			"list_type": "CONDUIT_UL_SceneActorsList",
			"list_id": "conduit_actors",
			"data": (ctx.workspace, "conduit_actors"),
			"data_active_index": (ctx.workspace, "conduit_actors_active_index"),
		}

		col = row.column()
		col.template_list(
			template_list_options["list_type"],
			template_list_options["list_id"],
			template_list_options["data"][0],
			template_list_options["data"][1],
			template_list_options["data_active_index"][0],
			template_list_options["data_active_index"][1],
			rows=1,
		)

		col = row.column(align=True)
		col.operator(SceneActorAddOperator.bl_idname, icon='ADD', text="")
		col.operator(SceneActorRemoveOperator.bl_idname, icon='REMOVE', text="")

		#  if ctx.workspace.conduit_actors and ctx.workspace.conduit_actors_active_index >= 0:
		#    item = ctx.workspace.conduit_actors[ctx.workspace.conduit_actors_active_index]
		#    row = self.layout.row()
		#    row.prop(item, "placeholder")


class CONDUIT_UL_SceneActorsList(bpy.types.UIList):
	def draw_item(self, ctx, layout, data, item, icon, active_data, active_property):
		layout.prop(item, "name", text="", icon="EMPTY_AXIS")
		layout.prop(item, "placeholder", text="", icon="META_CUBE")


class SceneActorAddOperator(bpy.types.Operator):
	bl_idname = "conduit.scene_actors_add"
	bl_label = "Add a new actor type"

	def execute(self, ctx):
		ctx.workspace.conduit_actors.add()
		return {'FINISHED'}


class SceneActorRemoveOperator(bpy.types.Operator):
	bl_idname = "conduit.scene_actors_remove"
	bl_label = "Remove an existing actor type"

	def execute(self, ctx):
		ctx.workspace.conduit_actors.remove(ctx.workspace.conduit_actors_active_index)
		return {'FINISHED'}


class ObjectDataPropertiesPanel(bpy.types.Panel):
	bl_idname = "CONDUIT_PT_object_panel"
	bl_label = "Conduit"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"

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


def object_actor_items(self, ctx):
	if not ctx:
		return []

	items = [(ACTOR_NONE, 'None', '')]
	for actor in ctx.workspace.conduit_actors:
		name = actor.name
		items.append((name, name, ''))
	return items


def object_actor_update(self, ctx):
	object_update_placeholder(self, ctx)


def register():
	# types
	bpy.utils.register_class(SceneActorProperty)

	# props
	bpy.types.WorkSpace.conduit_export_path = \
		bpy.props.StringProperty(subtype='DIR_PATH', default="//")
	bpy.types.WorkSpace.conduit_actors = \
		bpy.props.CollectionProperty(type=SceneActorProperty)
	bpy.types.WorkSpace.conduit_actors_active_index = \
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
	bpy.utils.register_class(ObjectDataPropertiesPanel)
	bpy.utils.register_class(WorkspacePanel)


def unregister():
	# panels
	bpy.utils.unregister_class(ObjectDataPropertiesPanel)
	bpy.utils.unregister_class(WorkspacePanel)

	# ui
	bpy.utils.unregister_class(CONDUIT_UL_SceneActorsList)

	# actions
	bpy.utils.unregister_class(ExportOperator)
	bpy.utils.unregister_class(SceneActorAddOperator)
	bpy.utils.unregister_class(SceneActorRemoveOperator)

	# props
	del bpy.types.WorkSpace.conduit_export_path
	del bpy.types.WorkSpace.conduit_actors
	del bpy.types.WorkSpace.conduit_actors_active_index
	del bpy.types.Object.conduit_actor

	# types
	bpy.utils.unregister_class(SceneActorProperty)
