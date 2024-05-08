#!/usr/bin/env python
import pika
import threading
import sys

def emit_log(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(f" [x] Sent {message}")

    connection.close()
#d
def receive_logs():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" {body}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

def main():
    thread_receive = threading.Thread(target=receive_logs)
    thread_receive.start()

    while True:
        # Leer la entrada del usuario desde la consola
        message = input("Ingrese un mensaje: ")

        # Transmitir el mensaje utilizando la función emit_log
        emit_log(message)

if __name__ == '__main__':
    main()
