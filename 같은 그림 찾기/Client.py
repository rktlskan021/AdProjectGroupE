import socket, threading
import pickle
m = [[0 for i in range(5)] for j in range(5)]
print(m)
def sendMsg(soc):
    while True:
        msg = input('')
        soc.sendall(msg.encode(encoding='utf-8'))
        if msg == '/stop':
            break
    print('클라이언트 메시지 입력 쓰레드 종료')

def recvMsg(soc):
    while True:
        data = soc.recv(1024)
        try:
            msg = pickle.loads(data)
        except:
            msg = data.decode()
        print(msg)
        if msg == '/stop':
            break
    soc.close()
    print('클라이언트 리시브 쓰레드 종료')

class Client:
    ip = 'localhost'
    port = 5000

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((Client.ip, Client.port))

    def run(self):
        t = threading.Thread(target=sendMsg, args=(self.client_socket,))
        t.start()
        t2 = threading.Thread(target=recvMsg, args=(self.client_socket,))
        t2.start()

client = Client()
client.run()
