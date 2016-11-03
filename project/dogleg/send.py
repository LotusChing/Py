# -*- coding:utf-8 -*-
import pika


class Center(object):
    def __init__(self):
        auth = pika.credentials.PlainCredentials(username='Lotus', password='Ching')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='120.24.80.34',
                    port=80,
                    credentials=auth))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='cmd')
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue
                                   )
    def on_response(self, ch, method, props, body):
        self.response = body

    def request(self, n):
        self.response = None
        self.channel.basic_publish(exchange='',
                                   routing_key='cmd',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue
                                        ),
                                   body=str(n)
                                   )
        while self.response is None:
            self.connection.process_data_events()
        return self.response.decode()


center = Center()
while True:
    commands = str(input('Please input commands: '))
    response = center.request(commands)
    print(response)
