import pika
import json
import subprocess


class Agent(object):
    def __init__(self):
        self.auth = pika.credentials.PlainCredentials(username='Lotus', password='Ching')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='120.24.80.34',
                    port=80,
                    credentials=self.auth))
        self.channel = self.connection.channel()

    def callback(self, ch, method, props, body):
        body=body.decode()
        parsed_json = json.loads(body)
        server, cmd = parsed_json['server'], parsed_json['cmd']
        commands = 'ssh ' + server + ' ' + cmd
        data, err = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(data)
                         )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('Response commands result to Queue.')

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='pek_cmd')
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

if __name__ == '__main__':
    try:
        agent = Agent()
        agent.consume()
    except KeyboardInterrupt:
        print('Exit.\n')
        exit()

