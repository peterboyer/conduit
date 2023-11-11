# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.connect(("127.0.0.1", 37020))

while True:
    data, addr = client.recvfrom(1024)
    print("received message: {}".format(data))
