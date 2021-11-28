import threading, socket

class Room: #채팅방
    def __init__(self):
        self.clients = []#접속한 클라이언트를 담당하는 ChatClient 객체 저장

    def addClient(self, c):#클라이언트 하나를 채팅방에 추가
        self.clients.append(c)
        print(self.clients)

    def delClent(self, c):#클라이언트 하나를 채팅방에서 삭제
        self.clients.remove(c)

    def sendAllClients(self, msg):
        for c in self.clients:
            c.sendMsg(msg)

class ChatClient:#텔레 마케터: 클라이언트 1명이 전송한 메시지를 받고, 받은 메시지를 다시 되돌려줌
    def __init__(self, id, soc, r):
        self.id = id    #클라이언트 id
        self.soc = soc  #담당 클라이언트와 1:1 통신할 소켓
        self.room = r   #채팅방 객체

    def recvMsg(self):
        while True:
            data = self.soc.recvs(1024)
            msg = data.decode()
            if msg == '/stop':
                self.sendMsg(msg) # 클라이언트쪽의 리시브 쓰레드 종료하라고..
                print(self.id,'님 퇴장')
                break

            msg = self.id+': ' + msg
            self.room.sendAllClients(msg)

        self.room.delClent(self)
        self.room.sendAllClients(self.id+'님이 퇴장하셨습니다.')


    def sendMsg(self, msg): #담당한 클라이언트 1명에게만 메시지 전송
        self.soc.sendall(msg.encode(encoding='utf-8'))

    def run(self):
        t = threading.Thread(target=self.recvMsg, args=())
        t.start()

class ServerMain:
    ip = 'localhost'
    port = 4444

    def __init__(self):
        self.room = Room()
        self.server_soc = None

    def open(self):
        self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_soc.bind((ServerMain.ip, ServerMain.port))
        self.server_soc.listen()

    def run(self):
        self.open()
        print('채팅 서버 시작')
        while True:
            c_soc, addr = self.server_soc.accept()
            print(addr)
            msg = '사용할 id:'
            c_soc.sendall(msg.encode(encoding='utf-8'))
            msg = c_soc.recvs(1024)
            id = msg.decode()
            cc = ChatClient(id, c_soc, self.room)
            self.room.addClient(cc)
            cc.run()
            print('클라이언트', id, '채팅 시작')

def main():
    server = ServerMain()
    server.run()

main()