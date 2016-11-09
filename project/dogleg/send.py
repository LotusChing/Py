import pika
import uuid
import json
deny_cmd = ['rm', 'dd', 'reboot', 'init', 'vim', 'service']
server_list = [
    '192.168.2.10',
    '192.168.2.20'
]

class Center(object):
    def __init__(self):
        auth = pika.credentials.PlainCredentials(username='user', password='pass')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='1.1.1.1',
                    port=1,
                    credentials=auth))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='cmd')
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        self.response = body

    def request(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='cmd',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id
                                        ),
                                   body=json.dumps(data)
                                   )
        while self.response is None:
            self.connection.process_data_events()
        return self.response

if __name__ == '__main__':
    try:
        center = Center()
        while True:
            for index, server in enumerate(server_list):
                print('{}. {}'.format(index, server))
            servers = str(input('Please choice Server: ')).split()
            commands = str(input('Commands: '))
            for server in servers:
                data = {
                    'server': server_list[int(server)],
                    'cmd': commands
                }
                response = center.request(data).decode()
                print('Server: {}\n Result: {}'.format(server_list[int(server)], response))
    except KeyboardInterrupt:
        print('Exit.\n')
        exit()

