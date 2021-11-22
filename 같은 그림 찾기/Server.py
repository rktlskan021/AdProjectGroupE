import sys
import socket
import threading
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout,
                             QVBoxLayout, QApplication, QHBoxLayout, QToolButton, QSizePolicy)
from PyQt5 import QtGui
from image import imageList, imageB, imageChange

import pickle

ip = ''
port = 5000

m = [[0 for i in range(5)] for j in range(5)]
m[0][1] = 1

class Button(QToolButton):

    def __init__(self, icon, callback, name):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setIcon(QtGui.QIcon(icon))
        self.setObjectName(name)
        self.clicked.connect(callback)

    def sizeHint(self):
        size = super(Button, self).sizeHint()
        size.setHeight(size.height() + 20)
        size.setWidth(max(size.width(), size.height()))
        return size

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.s = Server(self)
        self.initUI()
        self.gamePlayer = []
        self.startServer()

    def initUI(self):
        # self.player1 = QLabel('player1')
        # self.player2 = QLabel('player2')
        #
        # hBoxLayout = QHBoxLayout()
        # hBoxLayout.addWidget(self.player1)
        # hBoxLayout.addWidget(self.player2)

        self.imageLayout = QGridLayout()
        r = 0; c = 0
        for i, path in enumerate(imageList):
            imageB[i] = True
            button = Button("", self.buttonClicked, path)
            self.imageLayout.addWidget(button, r, c)
            c += 1
            if c >= 4:
                c = 0
                r += 1

        vBoxLatout = QVBoxLayout()
        # vBoxLatout.addLayout(hBoxLayout)
        vBoxLatout.addLayout(self.imageLayout)

        self.setLayout(vBoxLatout)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Server')
        self.show()

    def buttonClicked(self):
        key = self.sender()
        numberKey = self.imageLayout.indexOf(key)
        imageKey = imageB[numberKey] = not imageB[numberKey]
        self.sender().setIcon(QtGui.QIcon(imageChange[numberKey][imageKey]))

    def startServer(self):
        self.s.open()

    def addPlayer(self, c):
        self.gamePlayer.append(c)
        # self.send(self.gamePlayer, m)
        # self.setPlayerLabel()
        cc = Client(c, self)
        cc.run()

    # def setPlayerLabel(self):
    #     if len(self.gamePlayer) == 1:
    #         self.player1.setText(self.gamePlayer[0][1])
    #     elif len(self.gamePlayer) == 2:
    #         self.player2.setText(self.gamePlayer[1][1])

    def send(self, msg):
        try:
            data = pickle.dumps(msg)
        except:
            data = msg.decode()
        for i in self.gamePlayer:
            i.sendall(data)

    def changeImage(self, info):
        numberKey = info[0]
        imageKey = info[1]
        self.imageLayout.itemAt(numberKey).widget().setIcon(QtGui.QIcon(imageChange[numberKey][imageKey]))
        self.send(info)

    def delClient(self, c):
        c.close()
        self.gamePlayer.remove(c)
# class Client:
#     def __init__(self, id, soc):
#         self.id = id
#         self.soc = soc
#
#     def recvMsg(self):
#         while True:
#             data = self.soc.recv(1024)
#             msg = data.decode()
#             msg = self.id + ': ' + msg
#
#     def sendMsg(self, msg):  # 담당한 클라이언트 1명에게만 메시지 전송
#         self.soc.sendall(msg.encode(encoding='utf-8'))
#
#     def run(self):
#         t = threading.Thread(target=self.recvMsg, args=())
#         t.start()

class Client:
    def __init__(self, soc, r):
        self.soc = soc
        self.r = r

    def recv(self):
        while True:
            data = self.soc.recv(1024)
            try:
                msg = pickle.loads(data)
            except:
                msg = data.decode()
            self.r.changeImage(msg)

        self.r.delClient(self)

    def run(self):
        t = threading.Thread(target=self.recv, args=())
        t.start()

class Server:
    def __init__(self, ui):
        self.server_socket = None
        self.ui = ui

    def open(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.t = threading.Thread(target=self.listen, args=())
        self.t.start()

    def listen(self):
        print("서버시작")
        while True:
            self.server_socket.listen(2)
            client, addr = self.server_socket.accept()
            print(addr)
            # msg = '사용할 id:'
            # client.sendall(msg.encode(encoding='utf-8'))
            # msg = client.recv(1024)
            # id = msg.decode()
            # self.ui.addPlayer(client, id)
            self.ui.addPlayer(client)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Example()
    sys.exit(app.exec_())
