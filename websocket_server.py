import bpy
import threading
import socketserver

bl_info = {
    "name": "Avalon",
    "blender": (2, 80, 0),
    "category": "Import-Export"
}


# events

def on_object_transform(object, scene):
    print("on_object_transform", object.name, scene.name)


def on_object_transform_complete(object, scene):
    print("on_object_transform_complete", object.name, scene.name)


# https://blender.stackexchange.com/a/283286
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

# server

server = None


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("avalon:server:handle")
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())


def server_start():
    global server
    if server:
        return

    HOST, PORT = "localhost", 9999
    server = socketserver.TCPServer((HOST, PORT), RequestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()


def server_stop():
    global server
    if not server:
        return

    server.shutdown()
    server = None


# plugin

options = {
    "server": False
}


def register():
    print("avalon:register")
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

    if options["server"]:
        server_start()


def unregister():
    print("avalon:unregister")
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

    if options["server"]:
        server_stop()
