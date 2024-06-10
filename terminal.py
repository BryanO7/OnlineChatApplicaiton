import grpc
import subprocess
import threading
from concurrent import futures
from GroupChat import GroupChat
import chat_unificado_pb2
import chat_unificado_pb2_grpc
import privado_pb2
import privado_pb2_grpc
from private_chat_combined import PrivateChat
from Server import ChatService, NameServer

class ChatClient:
    def __init__(self, host='localhost', unified_port=50051):
        self.unified_channel = grpc.insecure_channel(f'{host}:{unified_port}')
        self.unified_stub = chat_unificado_pb2_grpc.ChatServiceStub(self.unified_channel)
        self.private_channel = grpc.insecure_channel(f'{host}:{unified_port}')
        self.private_stub = privado_pb2_grpc.PrivadoServiceStub(self.private_channel)

    # Group Chat Methods
    def register_client(self, username):
        request = chat_unificado_pb2.ClientRequest(username=username)
        response = self.unified_stub.RegisterClient(request)
        return response

    def subscribe_group_chat(self, chat_id, queue_name):
        return self.unified_stub.SubscribeGroupChat(chat_unificado_pb2.ChatSubscriptionRequest(chat_id=chat_id, queue_name=queue_name))

    def discover_chats(self):
        return self.unified_stub.DiscoverChats(chat_unificado_pb2.Empty())

    def list_clients(self):
        return self.unified_stub.ListUsers(chat_unificado_pb2.Empty())

    def chat_exists(self, chat_id):
        chats = self.discover_chats()
        return any(chat.chat_id == chat_id for chat in chats.chats)

    def establish_connection(self, username, target_username):
        request = chat_unificado_pb2.ConnectionRequest(username=username, target_username=target_username)
        response = self.unified_stub.EstablishConnection(request)
        if response.status.code == chat_unificado_pb2.ResponseStatus.OK:
            return response.endpoint
        else:
            print(f"Error: {response.status.message}")
            return None

    def send_message_to_user(self, username, target_username, message):
        return self.unified_stub.SendMessageToUser(
            chat_unificado_pb2.PrivateMessageRequest(username=username, target_username=target_username, message=message))

    def receive_messages_from_user(self, username):
        responses = self.unified_stub.ReceiveMessagesFromUser(chat_unificado_pb2.UserRequest(username=username))
        for response in responses:
            print(f"{response.username}: {response.message}")

    # Private Chat Methods
    def register_user(self, username, port):
        request = privado_pb2.User(username=username, port=port)
        response = self.private_stub.RegisterUser(request)
        return response

    def get_user_port(self, username):
        request = privado_pb2.UserRequest(username=username)
        response = self.private_stub.GetUserPort(request)
        return response

    def send_message(self, sender, recipient, content):
        request = privado_pb2.Message(sender=sender, recipient=recipient, content=content)
        response = self.private_stub.SendMessage(request)
        return response

class Terminal:
    def __init__(self, chat_client, group_chat):
        self.chat_client = chat_client
        self.group_chat = group_chat
        self.username = None
        self.listener_thread = None
        self.private_chat = None
        self.run_terminal()

    def run_terminal(self):
        self.username = input("Enter your username: ")
        response = self.chat_client.register_client(self.username)
        print(response)
        if response.endpoint and response.endpoint.port > 0:
            self.private_chat = PrivateChat(self.username, response.endpoint.port)
            self.private_chat.start_listening()
            print(f"Client registered with message: '{response.message}' at {response.endpoint.ip}:{response.endpoint.port}")
        else:
            print("Registration failed: ", response.message)

        self.menu_options()

    def menu_options(self):
        while True:
            print("\nOptions:")
            print("1. Connect group chat")
            print("2. Subscribe to group chat")
            print("3. Discover chats")
            print("4. Start private chat")
            print("5. List all clients")
            print("6. Exit")
            choice = input("Choose an option (1-6): ")

            if choice == '1':
                self.connect_group_chat()
            elif choice == '2':
                self.subscribe_group_chat()
            elif choice == '3':
                self.discover_chats()
            elif choice == '4':
                self.start_private_chat()
            elif choice == '5':
                self.list_all_clients()
            elif choice == '6':
                print("Exiting the application. Goodbye!")
                break
            else:
                print("Invalid option. Please select from 1-6.")

    def connect_group_chat(self):
        chat_id = input("Enter chat ID to connect: ")
        queue_name = input("Enter queue name to connect: ")
        if self.chat_client.chat_exists(chat_id):
            self.open_new_terminal(chat_id, queue_name)
        else:
            print("Chat does not exist.")
            return

    def subscribe_group_chat(self):
        group_id = input("Enter group chat ID to subscribe: ")
        queue_name = input("Enter queue name to subscribe: ")
        response = self.chat_client.subscribe_group_chat(group_id, queue_name)
        print(response.message)

    def discover_chats(self):
        response = self.chat_client.discover_chats()
        print("Available chats:")
        for chat in response.chats:
            print(f"Group Name: {chat.chat_id}")

    def start_private_chat(self):
        target_username = input("Enter the username of the person you want to chat with: ")
        endpoint = self.chat_client.establish_connection(self.username, target_username)
        if endpoint is None:
            print("No se pudo establecer la conexión.")
            return

        target_socket = self.private_chat.connect_to_user(endpoint.ip, endpoint.port)
        while True:
            message = input()
            if message.lower() == 'exit':
                break
            target_socket.send(message.encode('utf-8'))

    def list_all_clients(self):
        response = self.chat_client.list_clients()
        for client in response.users:
            print(f"Username: {client.username}, IP: {client.ip}, Port: {client.port}")

    def open_new_terminal(self, chat_id, queue_name):
        subprocess.Popen(['gnome-terminal', '--', 'python3', 'GroupChat.py', chat_id, queue_name])

    def start_listener(self, port):
        name_server = NameServer()
        chat_service = ChatService(name_server)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_unificado_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"Listening for incoming messages on port {port}")
        server.wait_for_termination()

if __name__ == "__main__":
    chat_client = ChatClient()
    group_chat = GroupChat()
    terminal = Terminal(chat_client, group_chat)
