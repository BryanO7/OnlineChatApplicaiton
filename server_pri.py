import grpc
from concurrent import futures
import time
import socket

import privado_pb2
import privado_pb2_grpc

users = {}
pending_messages = {}

class PrivadoService(privado_pb2_grpc.PrivadoServiceServicer):

    def RegisterUser(self, request, context):
        users[request.username] = request.port
        return privado_pb2.Response(message=f"User {request.username} registered with port {request.port}")

    def GetUserPort(self, request, context):
        port = users.get(request.username, "")
        return privado_pb2.UserResponse(port=str(port))

    def SendMessage(self, request, context):
        recipient = request.recipient
        if recipient in users:
            recipient_port = users[recipient]
            send_direct_message(request.sender, recipient, recipient_port, request.content)
            return privado_pb2.Response(message="Message sent")
        else:
            if recipient not in pending_messages:
                pending_messages[recipient] = []
            pending_messages[recipient].append((request.sender, request.content))
            return privado_pb2.Response(message="User not online. Message stored")

def send_direct_message(sender, recipient, port, message):
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(('localhost', int(port)))
        target_socket.send(f"Message from {sender}: {message}".encode())
        target_socket.close()
    except Exception as e:
        print(f"Error sending message to {recipient}: {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    privado_pb2_grpc.add_PrivadoServiceServicer_to_server(PrivadoService(), server)
    server.add_insecure_port('[::]:9999')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
