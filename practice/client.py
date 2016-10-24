# coding:utf8
__author__ = 'LotusChing'

from socketserver import BaseRequestHandler, TCPServer
import subprocess

class EchoHandler(BaseRequestHandler):
    def handle(self):
        print('Got connection from {}'.format(self.client_address))
        while True:
            cmd = self.request.recv(8192)
            if not cmd:
                self.request.send('Input is none.')
            print(cmd)
            data, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print(data)
            if err.decode() != '':
                self.request.send(err)
            if data.decode() == '':
                self.request.send(b'OK.')
            else:
                self.request.send(data)

if __name__ == '__main__':
    serv = TCPServer(('', 20000), EchoHandler)
    serv.serve_forever()
