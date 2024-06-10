import threading

import grpc
from concurrent import futures
import chat_unificado_pb2
import chat_unificado_pb2_grpc


class PrivateChatClient:
    def __init__(self, username, target_username, host, port):
        self.username = username
        self.target_username = target_username
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = chat_unificado_pb2_grpc.ChatServiceStub(self.channel)

    def send_message_to_user(self, username, target_username, message):
        response = self.stub.SendMessageToUser(chat_unificado_pb2.PrivateMessageRequest(username=username, target_username=target_username, message=message))
        print(response.message)

    def receive_messages_from_user(self):
        print(f"Trying to receive messages from {self.target_username} at {self.host}:{self.port}")
        try:
            responses = self.stub.ReceiveMessagesFromUser(chat_unificado_pb2.Empty())
            for response in responses:
                print(f"{response.username}: {response.message}")
        except grpc.RpcError as e:
            print(f"Error receiving messages: {e.details()} (code: {e.code})")
