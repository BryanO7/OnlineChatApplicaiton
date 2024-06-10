import grpc
import privado_pb2
import privado_pb2_grpc
import threading
import socket

class PrivateChat:
    def __init__(self, username, port):
        self.username = username
        self.port = port
        self.listen_socket = None

    def receive_messages(self, sock):
        while True:
            try:
                message = sock.recv(1024).decode('utf-8', errors='replace')
                if message:
                    print(f"Received: {message}")
            except Exception as e:
                print(f"An error occurred while receiving messages: {e}")
                sock.close()
                break

    def listen_for_incoming_connections(self):
        while True:
            client_socket, addr = self.listen_socket.accept()
            threading.Thread(target=self.receive_messages, args=(client_socket,)).start()

    def start_listening(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('localhost', self.port))
        self.listen_socket.listen(1)
        print(f"Listening on port {self.port}")
        threading.Thread(target=self.listen_for_incoming_connections).start()

    def connect_to_user(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, int(port)))
        threading.Thread(target=self.receive_messages, args=(client_socket,), daemon=True).start()
        return client_socket

    def register_user(self, stub):
        response = stub.RegisterUser(privado_pb2.User(username=self.username, port=self.port))
        print(response.message)

    def get_user_port(self, stub, target_user):
        response = stub.GetUserPort(privado_pb2.UserRequest(username=target_user))
        return response.port

    def send_message_to_user(self, stub, sender, recipient, message):
        response = stub.SendMessage(privado_pb2.Message(sender=sender, recipient=recipient, content=message))
        print(response.message)
