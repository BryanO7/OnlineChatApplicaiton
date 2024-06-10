import grpc
import subprocess
import threading
import socket
from concurrent import futures
from GroupChat import GroupChat
import chat_unificado_pb2
import chat_unificado_pb2_grpc
from private_chat_combined import PrivateChatClient

class ChatClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = chat_unificado_pb2_grpc.ChatServiceStub(self.channel)

    def register_client(self, username):
        request = chat_unificado_pb2.ClientRequest(username=username)
        response = self.stub.RegisterClient(request)
        return response

    def subscribe_group_chat(self, chat_id, queue_name):
        return self.stub.SubscribeGroupChat(chat_unificado_pb2.ChatSubscriptionRequest(chat_id=chat_id, queue_name=queue_name))

    def discover_chats(self):
        return self.stub.DiscoverChats(chat_unificado_pb2.Empty())

    def list_clients(self):
        return self.stub.ListUsers(chat_unificado_pb2.Empty())

    def chat_exists(self, chat_id):
        chats = self.discover_chats()
        return any(chat.chat_id == chat_id for chat in chats.chats)

    def establish_connection(self, username, target_username):
        request = chat_unificado_pb2.ConnectionRequest(username=username, target_username=target_username)
        response = self.stub.EstablishConnection(request)
        if response.status.code == chat_unificado_pb2.ResponseStatus.OK:
            return response.endpoint
        else:
            print(f"Error: {response.status.message}")
            return None

    def send_message_to_user(self, username, target_username, message):
        return self.stub.SendMessageToUser(
            chat_unificado_pb2.PrivateMessageRequest(username=username, target_username=target_username, message=message))

    def receive_messages_from_user(self, username):
        responses = self.stub.ReceiveMessagesFromUser(chat_unificado_pb2.UserRequest(username=username))
        for response in responses:
            print(f"{response.username}: {response.message}")

class Terminal:
    def __init__(self, chat_client, group_chat):
        self.chat_client = chat_client
        self.group_chat = group_chat
        self.username = None
        self.listener_thread = None
        self.run_terminal()

    def run_terminal(self):
        self.username = input("Enter your username: ")
        response = self.chat_client.register_client(self.username)
        print(response)  # Log the response to debug
        if response.endpoint and response.endpoint.port > 0:
            print(f"Client registered with message: '{response.message}' at {response.endpoint.ip}:{response.endpoint.port}")
            # Start the listener thread
            self.listener_thread = threading.Thread(target=self.start_listener, args=(response.endpoint.port,))
            self.listener_thread.start()
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

        private_chat_client = PrivateChatClient(self.username, target_username, endpoint.ip, endpoint.port)
        threading.Thread(target=private_chat_client.receive_messages_from_user, daemon=True).start()

        while True:
            message = input()
            if message.lower() == 'exit':
                break
            private_chat_client.send_message_to_user(self.username, target_username, message)

    def list_all_clients(self):
        response = self.chat_client.list_clients()
        for client in response.users:
            print(f"Username: {client.username}, IP: {client.ip}, Port: {client.port}")

    def open_new_terminal(self, chat_id, queue_name):
        subprocess.Popen(['gnome-terminal', '--', 'python3', 'GroupChat.py', chat_id, queue_name])

    def start_listener(self, port):
        host = 'localhost'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print(f"Listening for incoming messages on {host}:{port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        try:
                            print(f"Message from {addr}: {data.decode()}")
                        except UnicodeDecodeError:
                            print(f"Binary message from {addr}: {data}")

if __name__ == "__main__":
    chat_client = ChatClient()
    group_chat = GroupChat()
    terminal = Terminal(chat_client, group_chat)
