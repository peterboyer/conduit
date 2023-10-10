bl_info = {
    "name": "Avalon",
    "blender": (2, 80, 0),
    "category": "Import-Export"
}

import threading
import socketserver

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("avalon:server:handle")
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())

server = None

def register():
    print("avalon:register")

    global server
    if server:
        return

    HOST, PORT = "localhost", 9999
    server = socketserver.TCPServer((HOST, PORT), RequestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

def unregister():
    print("avalon:unregister")

    global server
    if not server:
        return

    server.shutdown()
    server = None
