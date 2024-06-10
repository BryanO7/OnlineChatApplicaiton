import grpc
import privado_pb2
import privado_pb2_grpc
import threading
import socket


class PrivateChat:
    def __init__(self, username, target_username, host, port, private_port):
        self.username = username
        self.target_username = target_username
        self.host = host
        self.port = port
        self.private_port = private_port
        self.channel = grpc.insecure_channel(f'{host}:{private_port}')
        self.stub = privado_pb2_grpc.PrivadoServiceStub(self.channel)
        self.listen_socket = None

    def receive_messages(self, sock):
        while True:
            try:
                message = sock.recv(1024)
                if message:
                    print(f"Received: {message.decode('utf-8', errors='replace')}")
            except Exception as e:
                print(f"An error occurred while receiving messages: {e}")
                sock.close()
                break

    def listen_for_incoming_connections(self):
        while True:
            client_socket, addr = self.listen_socket.accept()
            threading.Thread(target=self.receive_messages, args=(client_socket,)).start()

    def register_user(self):
        response = self.stub.RegisterUser(privado_pb2.User(username=self.username, port=self.port))
        print(response.message)

    def get_user_port(self, target_user):
        response = self.stub.GetUserPort(privado_pb2.UserRequest(username=target_user))
        return response.port

    def send_message_to_user(self, sender, recipient, message):
        response = self.stub.SendMessage(privado_pb2.Message(sender=sender, recipient=recipient, content=message))
        print(response.message)

    def connect_to_user(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, int(port)))
        threading.Thread(target=self.receive_messages, args=(client_socket,)).start()
        return client_socket

    def start_listening(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(('localhost', self.port))
        self.listen_socket.listen(1)
        print(f"Listening on port {self.port}")
        threading.Thread(target=self.listen_for_incoming_connections).start()
