import pika
import uuid
deny_cmd = ['rm', 'dd', 'reboot', 'init', 'vim', 'service']


class Center(object):
    def __init__(self):
        auth = pika.credentials.PlainCredentials(username='Da', password='Da')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='1.1.1.1',
                    port=80,
                    credentials=auth))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='cmd')
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        self.response = body

    def request(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='cmd',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id
                                        ),
                                   body=str(n)
                                   )
        while self.response is None:
            self.connection.process_data_events()
        return self.response

if __name__ == '__main__':
    try:
        center = Center()
        while True:
            commands = str(input('Please input commands: '))
            response = center.request(commands).decode()
            print(response)
    except KeyboardInterrupt:
        print('Exit.\n')
        exit()
