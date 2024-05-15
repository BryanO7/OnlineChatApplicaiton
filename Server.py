import redis

class NameServer:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def register_client(self, username, ip_address, port):
        # Store client details as 'ip:port'
        self.redis_client.hset("chat_namespace", username, f"{ip_address}:{port}")

    def get_client_address(self, username):
        # Retrieve client details
        return self.redis_client.hget("chat_namespace", username)

    def all_chats(self):
        # Retrieve all chats and their details
        return self.redis_client.hgetall("chat_namespace")
