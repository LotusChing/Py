# -*- coding:utf-8 -*-
__author__ = "LotusChing"
import pika

auth = pika.credentials.PlainCredentials(username='Lotus', password='Ching')
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='120.24.80.34',
            port=80,
            credentials=auth))

channel = connection.channel()
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
