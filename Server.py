import redis
import socket


class NameServer:
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def register_client(self, username):
        ip_address = 'localhost'
        port = self.find_free_port()  # Encuentra un puerto libre
        self.redis_client.hset("clients", username, f"{ip_address}:{port}")
        print(f"Cliente {username} registrado con IP {ip_address} y puerto {port}")

    def get_client_address(self, username):
        # Retrieve client details
        return self.redis_client.hget("chat_namespace", username)

    def all_chats(self):
        # Retrieve all chats and their details
        return self.redis_client.hgetall("chat_namespace")

    def chat_exists(self, chat_id):
        # Check if chat exists
        return self.redis_client.hexists("chat_namespace", chat_id)

    def register_chat(self, chat_id):
        # Register chat
        self.redis_client.hset("chat_namespace", chat_id,"chat_group")


