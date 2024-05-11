from concurrent import futures

import grpc
import time

import grpc_pb2 as chat
import grpc_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer): 

    def init(self):
        self.chats = []

    def ChatStream(self, requestiterator, context):

        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        print("[{}] {}".format(request.name, request.message))
        self.chats.append(request)
        return chat.Empty()


if __name__ == '__main':
    port = 11912
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server) 
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)