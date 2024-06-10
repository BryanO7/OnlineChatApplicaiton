import redis
import socket
import grpc
from concurrent import futures
import chat_unificado_pb2
import chat_unificado_pb2_grpc
import privado_pb2
import privado_pb2_grpc
import pika
import time

pending_messages = {}

class ChatService(chat_unificado_pb2_grpc.ChatServiceServicer):
    def __init__(self, name_server):
        self.name_server = name_server
        self.messages = {}  # Almacena mensajes para cada usuario

    def RegisterClient(self, request, context):
        username = request.username
        port = self.name_server.find_free_port()
        self.name_server.register_client(username, port)
        endpoint = chat_unificado_pb2.NetworkEndpoint(ip='localhost', port=port)
        return chat_unificado_pb2.ClientResponse(message=f"Cliente {username} registrado en el puerto {port}", endpoint=endpoint)

    def GetClientAddress(self, request, context):
        address = self.name_server.get_client_address(request.username)
        if address:
            return chat_unificado_pb2.ClientResponse(message=f"Address: {address.decode()}")
        else:
            return chat_unificado_pb2.ClientResponse(message="Client not found")

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

    def DiscoverChats(self, request, context):
        raw_chats = self.name_server.all_chats()
        chat_infos = []
        for chat_id in raw_chats:
            chat_info = chat_unificado_pb2.ChatInfo(chat_id=chat_id.decode())
            chat_infos.append(chat_info)
        return chat_unificado_pb2.ChatListResponse(chats=chat_infos)

    def ListUsers(self, request, context):
        users = []
        clients = self.name_server.all_clients()
        for username, address in clients.items():
            ip, port = address.decode().split(":")
            user = chat_unificado_pb2.User(username=username, ip=ip, port=port)
            users.append(user)
        return chat_unificado_pb2.UserListResponse(users=users)

    def EstablishConnection(self, request, context):
        username = request.username
        target_username = request.target_username
        address = self.name_server.get_client_address(target_username)
        if address:
            ip, port = address.decode().split(':')
            return chat_unificado_pb2.ConnectionResponse(
                status=chat_unificado_pb2.ResponseStatus(
                    code=chat_unificado_pb2.ResponseStatus.OK,
                    message="Connection established"
                ),
                endpoint=chat_unificado_pb2.NetworkEndpoint(ip=ip, port=int(port))
            )
        else:
            return chat_unificado_pb2.ConnectionResponse(
                status=chat_unificado_pb2.ResponseStatus(
                    code=chat_unificado_pb2.ResponseStatus.NOT_FOUND,
                    message="User not found"
                )
            )

    def SendMessageToUser(self, request, context):
        username = request.username
        target_username = request.target_username
        message = request.message
        if target_username not in self.messages:
            self.messages[target_username] = []
        self.messages[target_username].append(chat_unificado_pb2.PrivateMessageResponse(username=username, message=message))
        return chat_unificado_pb2.PrivateMessageResponse(message="Message sent")

    def ReceiveMessagesFromUser(self, request, context):
        username = request.username
        if username in self.messages:
            while self.messages[username]:
                message = self.messages[username].pop(0)
                yield message
        else:
            yield chat_unificado_pb2.PrivateMessageResponse(username=username, message="No new messages")

class PrivadoService(privado_pb2_grpc.PrivadoServiceServicer):
    def __init__(self, name_server):
        self.name_server = name_server

    def RegisterUser(self, request, context):
        username = request.username
        port = request.port
        self.name_server.register_client(username, port)
        return privado_pb2.Response(message=f"User {username} registered with port {port}")

    def GetUserPort(self, request, context):
        address = self.name_server.get_client_address(request.username)
        if address:
            _, port = address.decode().split(":")
            return privado_pb2.UserResponse(port=port)
        else:
            return privado_pb2.UserResponse(port="")

    def SendMessage(self, request, context):
        recipient = request.recipient
        address = self.name_server.get_client_address(recipient)
        if address:
            _, port = address.decode().split(":")
            send_direct_message(request.sender, recipient, port, request.content)
            return privado_pb2.Response(message="Message sent")
        else:
            # Store message if recipient is not online
            if recipient not in pending_messages:
                pending_messages[recipient] = []
            pending_messages[recipient].append((request.sender, request.content))
            return privado_pb2.Response(message="User not online. Message stored")

def send_direct_message(sender, recipient, port, message):
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(('localhost', int(port)))
        target_socket.send(f"Message from {sender}: {message}".encode('utf-8'))
        target_socket.close()
    except Exception as e:
        print(f"Error sending message to {recipient}: {e}")


class NameServer:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def register_client(self, username, port):
        ip_address = 'localhost'
        self.redis_client.hset("clients", username, f"{ip_address}:{port}")
        print(f"Cliente {username} registrado con IP {ip_address} y puerto {port}")

    def get_client_address(self, username):
        return self.redis_client.hget("clients", username)

    def all_chats(self):
        return self.redis_client.smembers("chats")

    def all_clients(self):
        return self.redis_client.hgetall("clients")

    def chat_exists(self, chat_id):
        return self.redis_client.sismember("chats", chat_id)

    def register_chat(self, chat_id):
        self.redis_client.sadd("chats", chat_id)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_server = NameServer()

    chat_service = ChatService(name_server)
    privado_service = PrivadoService(name_server)

    chat_unificado_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)
    privado_pb2_grpc.add_PrivadoServiceServicer_to_server(privado_service, server)

    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started and listening on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
