# coding:utf8
import socket
import readline
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 20000))

while True:
    inp = input('Please input: ').encode()
    s.send(inp)
    ret = s.recv(8192)
    if ret == '':
        continue
    else:
        print(ret.decode())
