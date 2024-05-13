#!/usr/bin/env python
#new branch
import pika
import threading
import sys
from Server import ChatServer
from functools import partial

def emit_log(chat_id,message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    exchange_name = f'logs_{chat_id}'

    channel.exchange_declare(exchange='exchange_name', exchange_type='fanout')

    channel.basic_publish(exchange='exchange_name', routing_key='', body=message)
    print(f" [x] Sent {message}")

    connection.close()
#d
def receive_logs(chat_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declara un exchange para el chat específico usando la ID del chat
    exchange_name = f'logs_{chat_id}'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    # Declara una cola única para este chat
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Hace el bind de la cola al exchange del chat específico
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print(f'[*] Esperando mensajes para el chat {chat_id}. Para salir, presiona CTRL+C')

    def callback(ch, method, properties, body):
        print(f"Mensaje recibido en el chat {chat_id}: {body}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    # Empieza a consumir mensajes
    channel.start_consuming()


def main():
    server2 = ChatServer()
    server2.add_chat("grupo1", "127.0.0.1", 8000)
    server_ip = server2.get_chat_address("grupo1")

    thread_receive = threading.Thread(target=receive_logs, args=(server_ip,))
    thread_receive.start()

    while True:
        # Leer la entrada del usuario desde la consola
        message = input("Ingrese un mensaje: ")
        # Transmitir el mensaje utilizando la función emit_log
        emit_log(message,server_ip)

if __name__ == '__main__':
    main()
