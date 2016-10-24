# coding:utf8
__author__ = 'LotusChing'

from socketserver import BaseRequestHandler, TCPServer
import subprocess

class EchoHandler(BaseRequestHandler):
    def handle(self):
        print('Got connection from {}'.format(self.client_address))
        while True:
            msg = self.request.recv(8192)
            if not msg:
                self.request.send('Input is none.')
            data, err = subprocess.Popen('ls', stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if err.decode() is None:
                self.request.send(data.data)
            else:
                self.request.send(b'Error')

if __name__ == '__main__':
    serv = TCPServer(('', 20000), EchoHandler)
    serv.serve_forever()