import grpc
import subprocess
import threading
from GroupChat import GroupChat
import chat_unificado_pb2
import chat_unificado_pb2_grpc
from private_chat_combined import PrivateChatClient, serve as serve_private, start_receiving

class ChatClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = chat_unificado_pb2_grpc.ChatServiceStub(self.channel)

    def register_client(self, username):
        return self.stub.RegisterClient(chat_unificado_pb2.ClientRequest(username=username))

    def subscribe_group_chat(self, chat_id, queue_name):
        return self.stub.SubscribeGroupChat(chat_unificado_pb2.ChatSubscriptionRequest(chat_id=chat_id, queue_name=queue_name))

    def discover_chats(self):
        return self.stub.DiscoverChats(chat_unificado_pb2.Empty())

    def list_clients(self):
        return self.stub.ListUsers(chat_unificado_pb2.Empty())

    def chat_exists(self, chat_id):
        chats = self.discover_chats()
        return any(chat.chat_id == chat_id for chat in chats.chats)


class Terminal:
    def __init__(self, chat_client, group_chat):
        self.chat_client = chat_client
        self.group_chat = group_chat
        self.username = None
        self.run_terminal()

    def run_terminal(self):
        self.username = input("Enter your username: ")
        response = self.chat_client.register_client(self.username)
        print(response.message)

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
        print("por hacer")

    def list_all_clients(self):
        response = self.chat_client.list_clients()
        for client in response.users:
           print(f"Username: {client.username}, IP: {client.ip}, Port: {client.port}")

    def open_new_terminal(self, chat_id, queue_name):
        subprocess.Popen(['gnome-terminal', '--', 'python3', 'GroupChat.py', chat_id, queue_name])


if __name__ == "__main__":
    chat_client = ChatClient()
    group_chat = GroupChat()
    terminal = Terminal(chat_client, group_chat)

    # Start the gRPC server for private chat
    server = serve_private()
    print("Private chat server started.")

    server.wait_for_termination()
