import redis
import socket
import grpc
from concurrent import futures
import chat_unificado_pb2
import chat_unificado_pb2_grpc
import pika
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ChatService(chat_unificado_pb2_grpc.ChatServiceServicer):
    def __init__(self, name_server):
        self.name_server = name_server

    def RegisterClient(self, request, context):
        username = request.username
        self.name_server.register_client(username)
        return chat_unificado_pb2.ClientResponse(message=f"Cliente {username} registrado")

    def GetClientAddress(self, request, context):
        address = self.name_server.get_client_address(request.username)
        return chat_unificado_pb2.ClientResponse(message=f"Address: {address}")

    def SubscribeGroupChat(self, request, context):
        chat_id = request.chat_id
        queue_name = request.queue_name
        if not self.name_server.chat_exists(chat_id):
            self.name_server.register_chat(chat_id)
            print(f"New chat {chat_id} created.")
        else:
            print(f"Chat {chat_id} already exists.")
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        exchange_name = f'group_chat_{chat_id}'
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name, queue=queue_name)
        connection.close()
        return chat_unificado_pb2.ChatResponse(message=f"Subscribed to chat {chat_id} with queue {queue_name}")

    def ListUsers(self, request, context):
        logging.debug("ListUsers called")
        try:
            client_data = self.name_server.get_all_clients()  # Asumiendo que name_server es accesible y tiene este método
            users = []
            for username, address in client_data.items():
                # Decodificar tanto el username como la dirección IP y el puerto
                username = username.decode('utf-8')  # Decodifica el username de bytes a str
                address = address.decode('utf-8')  # Decodifica la dirección de bytes a str

                ip, port = address.split(':')  # Ahora address es un str, split debería funcionar
                user = chat_unificado_pb2.User(username=username, ip=ip, port=port)
                users.append(user)
            logging.debug(f"Users listed: {users}")
            return chat_unificado_pb2.UserListResponse(users=users)
        except Exception as e:
            logging.er
    def DiscoverChats(self, request, context):
        raw_chats = self.name_server.all_chats()
        chat_infos = []
        for chat_id in raw_chats:
            chat_info = chat_unificado_pb2.ChatInfo(
                chat_id=chat_id.decode()
            )
            chat_infos.append(chat_info)
        return chat_unificado_pb2.ChatListResponse(chats=chat_infos)

class NameServer:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def register_client(self, username):
        ip_address = 'localhost'
        port = self.find_free_port()
        self.redis_client.hset("clients", username, f"{ip_address}:{port}")
        print(f"Cliente {username} registrado con IP {ip_address} y puerto {port}")

    def get_client_address(self, username):
        return self.redis_client.hget("clients", username)

    def get_all_clients(self):
        return self.redis_client.hgetall("clients")

    def all_chats(self):
        return self.redis_client.smembers("chats")

    def chat_exists(self, chat_id):
        return self.redis_client.sismember("chats", chat_id)

    def register_chat(self, chat_id):
        self.redis_client.sadd("chats", chat_id)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_server = NameServer()
    chat_service = ChatService(name_server)
    chat_unificado_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)
    server.add_insecure_port('[::]:50051')
    logging.info("Starting server on [::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
