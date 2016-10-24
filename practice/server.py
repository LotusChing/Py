# coding:utf8
__author__ = 'LotusChing'
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 20000))

while True:
    inp = input('Please input: ').encode()
    print(type(inp))
    s.send(inp)
    ret = s.recv(8192)
    print(ret)
