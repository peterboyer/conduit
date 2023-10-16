import bpy

bl_info = {
    "name": "Conduit",
    "blender": (2, 80, 0),
    "category": "Import-Export"
}


def on_object_transform(object, scene):
    pass


def on_object_transform_complete(object, scene):
    pass


def on_depsgraph_update(scene):
    depsgraph = bpy.context.evaluated_depsgraph_get()

    if on_depsgraph_update.operator is None:
        on_depsgraph_update.operator = bpy.context.active_operator

    for update in depsgraph.updates:
        if not update.is_updated_transform:
            continue

        object = bpy.context.active_object

        if on_depsgraph_update.operator is bpy.context.active_operator:
            on_object_transform(object, scene)
            continue

        on_object_transform_complete(object, scene)
        on_depsgraph_update.operator = None


on_depsgraph_update.operator = None


def register():
    print("register")
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    print("unregister")
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
