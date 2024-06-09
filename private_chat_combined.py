import grpc
import threading
from concurrent import futures
import private_chat_pb2
import private_chat_pb2_grpc

class PrivateChatService(private_chat_pb2_grpc.PrivateChatServiceServicer):
    def __init__(self):
        self.clients = {}  # Almacena las conexiones activas
        self.messages = {}  # Almacena los mensajes para cada cliente

    def EstablishConnection(self, request, context):
        username = request.username
        target_username = request.target_username
        if target_username not in self.clients:
            self.clients[target_username] = []  # Inicializa la lista de conexiones para el usuario objetivo
            self.messages[target_username] = []  # Inicializa la lista de mensajes para el usuario objetivo
        self.clients[target_username].append(username)
        return private_chat_pb2.ConnectionResponse(message=f"Connection established with {target_username}")

    def SendMessage(self, request, context):
        username = request.username
        target_username = request.target_username
        message = request.message
        if target_username in self.clients and username in self.clients[target_username]:
            self.messages[target_username].append((username, message))
            return private_chat_pb2.MessageResponse(username=username, message=message)
        return private_chat_pb2.MessageResponse(username="Server", message="Failed to send message")

    def ReceiveMessages(self, request, context):
        username = request.username
        if username in self.messages:
            while True:
                while self.messages[username]:
                    sender, message = self.messages[username].pop(0)
                    yield private_chat_pb2.MessageResponse(username=sender, message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    private_chat_pb2_grpc.add_PrivateChatServiceServicer_to_server(PrivateChatService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Private chat server started and listening on port 50052")
    return server

class PrivateChatClient:
    def __init__(self, username, target_username, host='localhost', port=50052):
        self.username = username
        self.target_username = target_username
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = private_chat_pb2_grpc.PrivateChatServiceStub(self.channel)

    def establish_connection(self):
        request = private_chat_pb2.ConnectionRequest(username=self.username, target_username=self.target_username)
        response = self.stub.EstablishConnection(request)
        print(response.message)

    def send_message(self, message):
        request = private_chat_pb2.MessageRequest(username=self.username, target_username=self.target_username, message=message)
        response = self.stub.SendMessage(request)
        print(f"{response.username}: {response.message}")

    def receive_messages(self):
        request = private_chat_pb2.Empty()
        responses = self.stub.ReceiveMessages(request)
        for response in responses:
            print(f"{response.username}: {response.message}")

def start_receiving(client):
    client.receive_messages()

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) != 3:
        print("Usage: python private_chat_combined.py <username> <target_username>")
        sys.exit(1)

    username = sys.argv[1]
    target_username = sys.argv[2]

    # Start the server
    server = serve()

    # Wait for a moment to ensure the server is fully started
    time.sleep(2)

    # Start the client
    client = PrivateChatClient(username, target_username)
    client.establish_connection()
    threading.Thread(target=start_receiving, args=(client,), daemon=True).start()

    while True:
        message = input()
        client.send_message(message)
