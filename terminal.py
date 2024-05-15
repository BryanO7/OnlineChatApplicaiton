# Terminal.py
import threading
from GroupChat import GroupChat

class Terminal:
    def __init__(self, name_server, group_chat):
        self.name_server = name_server
        self.group_chat = group_chat
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
        # Use GroupChat's consume method to handle connection and message passing
        self.group_chat.consume(chat_id)

    def subscribe_group_chat(self):
        group_id = input("Enter group chat ID to subscribe: ")
        if not self.name_server.chat_exists(group_id):
            print(f"Group chat '{group_id}' created.")
        else:
            print(f"Subscribing to existing group chat '{group_id}'.")

    # Add other methods as needed...

# Example usage
if __name__ == "__main__":
    from Server import NameServer  # Assuming correct import
    name_server = NameServer()
    group_chat = GroupChat()
    terminal = Terminal(name_server, group_chat)
