import redis

import redis

class ChatServer:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def register_client(self, username, ip_address, port):
        self.redis_client.hset("clients", username, f"{ip_address}:{port}")

    def get_client_address(self, username):
        return self.redis_client.hget("clients", username)

    def add_chat(self, chat_id, ip_address, port):
        chat_address = f"{ip_address}:{port}"
        self.redis_client.hset("chats", chat_id, chat_address)

    def get_chat_address(self, chat_id):
        chat_address = self.redis_client.hget("chats", chat_id)
        if chat_address:
            return tuple(chat_address.decode().split(':'))
        return None

    def get_all_chat_addresses(self):
        return self.redis_client.hgetall("chats")
# Ejemplo de uso#
#if __name__ == "__main__":
   # server = ChatServer()
#print("hola")
    # Registro automático de clientes
#    server.register_client("usuario1", "localhost", 12345)
#    server.register_client("usuario2", "localhost", 54321)

    # Obtener la dirección del cliente
 #   client_address = server.get_client_address("usuario1")
  #  print("Dirección del cliente usuario1:", client_address)

    # Agregar un chat
#server.add_chat("grupo1", "127.0.0.1", 8000)
#chat_address = server.get_chat_address("grupo1")
#print("Dirección del chat grupo1:", chat_address)  # Esto imprimirá ('127.0.0.1', '8000')

    # Obtener la dirección del chat
   # chat_address = server.get_chat_address("grupo1")
    #print("Dirección del chat grupo1:", chat_address)
