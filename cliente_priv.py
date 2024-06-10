import grpc
import privado_pb2
import privado_pb2_grpc
import threading
import socket

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                print(f"Received: {message}")
        except:
            print("An error occurred while receiving messages!")
            sock.close()
            break

def listen_for_incoming_connections(sock):
    while True:
        client_socket, addr = sock.accept()
        threading.Thread(target=receive_messages, args=(client_socket,)).start()

def register_user(stub, username, port):
    response = stub.RegisterUser(privado_pb2.User(username=username, port=port))
    print(response.message)

def get_user_port(stub, target_user):
    response = stub.GetUserPort(privado_pb2.UserRequest(username=target_user))
    return response.port

def send_message_to_user(stub, sender, recipient, message):
    response = stub.SendMessage(privado_pb2.Message(sender=sender, recipient=recipient, content=message))
    print(response.message)

def connect_to_user(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, int(port)))
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    return client_socket

def main():
    channel = grpc.insecure_channel('localhost:9999')
    stub = privado_pb2_grpc.PrivadoServiceStub(channel)

    username = input("Enter your username: ")
    port = int(input("Enter your port number (must be > 1024): "))
    if port <= 1024:
        print("Port number must be greater than 1024")
        return

    # Register user with the server
    register_user(stub, username, port)

    # Setup client socket to listen for incoming messages
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('localhost', port))
    listen_socket.listen(1)
    print(f"Listening on port {port}")

    threading.Thread(target=listen_for_incoming_connections, args=(listen_socket,)).start()

    while True:
        target_user = input("Enter the username of the user you want to connect to: ")

        # Connect to server to get the target user's port
        target_port = get_user_port(stub, target_user)

        if not target_port:
            print(f"User {target_user} not found. The message will be stored and delivered when the user is available.")
            message = input("Enter your message: ")
            send_message_to_user(stub, username, target_user, message)
            continue

        target_socket = connect_to_user('localhost', target_port)

        while True:
            message = input()
            if not message:
                break
            target_socket.send(message.encode())

if __name__ == "__main__":
    main()
