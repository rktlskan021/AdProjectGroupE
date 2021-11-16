import threading, socket

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
        msg = data.decode()
        print(msg)
        if msg == '/stop':
            break
    soc.close()
    print('클라이언트 리시브 쓰레드 종료')

class Client:
    ip = 'localhost'
    port = 4444

    def __init__(self):
        self.client_soc = None

    def conn(self):
        self.client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_soc.connect((Client.ip, Client.port))

    def run(self):
        self.conn()
        t = threading.Thread(target=sendMsg, args=(self.client_soc,))
        t.start()
        t2 = threading.Thread(target=recvMsg, args=(self.client_soc,))
        t2.start()

def main():
    c = Client()
    c.run()

main()