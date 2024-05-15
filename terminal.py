import threading
from Server import ChatServer

class Terminal:
    def __init__(self):
        server = ChatServer()
        self.username = None
        self.run_terminal()

    def run_terminal(self):
        self.username = input("Enter your username: ")

        while True:
            print("\nOptions:")
            print("1. Connect chat")
            print("2. Subscribe to group chat")
            print("3. Discover chats")
            print("4. Access insult channel")
            choice = input("Choose an option (1-4): ")

            if choice == '1':
                self.connect_chat()
            elif choice == '2':
                self.subscribe_group_chat()
            elif choice == '3':
                self.discover_chats()
            elif choice == '4':
                self.access_insult_channel()
            else:
                print("Invalid option. Please select from 1-4.")

    def connect_chat(self):
        chat_id = input("Enter chat ID to connect: ")
        # Assume a method to connect to chat; might need to handle group/private chats differently
        self.server.connect_to_chat(chat_id, self.username)

    def subscribe_group_chat(self):
        group_id = input("Enter group chat ID to subscribe: ")
        # Check if chat exists, create if not, and subscribe
        if not self.server.chat_exists(group_id):
            self.server.create_group_chat(group_id)
        self.server.subscribe_to_chat(group_id, self.username)

    def discover_chats(self):
        chats = self.server.get_all_chat_addresses()
        print("Active chats:")
        for chat_id, address in chats.items():
            print(f"Chat ID: {chat_id}, Address: {address}")

    def access_insult_channel(self):
        recipient = input("Enter recipient's username for the insult: ")
        insult = input("Enter your insult message: ")
        self.server.send_insult_message(recipient, insult)

# Example usage
if __name__ == "__main__":
    server = ChatServer()  # Assuming ChatServer is properly defined elsewhere
    terminal = Terminal()