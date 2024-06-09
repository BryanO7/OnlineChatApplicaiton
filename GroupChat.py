import pika
import threading
import sys
class GroupChat:
    def __init__(self, host='localhost'):
        self.host = host

    def connect_to_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()
        return connection, channel

    def receive_messages(self, group_name, queue_name):
        connection, channel = self.connect_to_rabbitmq()
        exchange_name = f'group_chat_{group_name}'
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name, queue=queue_name)

        def callback(ch, method, properties, body):
            print(f"[{group_name}] Received: {body.decode()}")

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(f"Joined group '{group_name}' on queue '{queue_name}'. Waiting for messages. To exit press CTRL+C")
        try:
            channel.start_consuming()
        finally:
            connection.close()

    def send_messages(self, group_name):
        connection, channel = self.connect_to_rabbitmq()
        exchange_name = f'group_chat_{group_name}'
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

        try:
            while True:
                message = input()
                if message.lower() == 'exit':
                    break
                channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
        finally:
            print("Exiting...")
            connection.close()

    def consume(self, group_name, queue_name):
        # Start a thread to receive messages for the specified group and queue
        threading.Thread(target=self.receive_messages, args=(group_name, queue_name), daemon=True).start()

        # Send messages from the main thread
        self.send_messages(group_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python GroupChat.py <group_name> <queue_name>")
        sys.exit(1)

    group_name = sys.argv[1]
    queue_name = sys.argv[2]

    group_chat = GroupChat()
    group_chat.consume(group_name, queue_name)
