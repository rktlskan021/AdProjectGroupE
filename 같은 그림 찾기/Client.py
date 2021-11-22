import sys
import socket
import threading
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QToolButton, QSizePolicy)
from PyQt5 import QtGui
from image import imageList, imageB, imageChange

import pickle
m = [[0 for i in range(5)] for j in range(5)]

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

def sendMsg(soc):
    while True:
        msg = input('')
        soc.sendall(msg.encode(encoding='utf-8'))
        if msg != '':
            break
    print('id 입력 완료')

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

class Client(QWidget):
    ip = 'localhost'
    port = 5000

    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((Client.ip, Client.port))


    def initUI(self):
        self.player1 = QLabel('player1')
        self.player2 = QLabel('player2')

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.player1)
        hBoxLayout.addWidget(self.player2)

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
        vBoxLatout.addLayout(hBoxLayout)
        vBoxLatout.addLayout(self.imageLayout)

        self.setLayout(vBoxLatout)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Client')
        self.show()

    def buttonClicked(self):
        key = self.sender()
        numberKey = self.imageLayout.indexOf(key)
        imageKey = imageB[numberKey] = not imageB[numberKey]
        self.sender().setIcon(QtGui.QIcon(imageChange[numberKey][imageKey]))
        self.send(numberKey, imageKey)

    def run(self):
        t = threading.Thread(target=sendMsg, args=(self.client_socket,))
        t.start()
        t2 = threading.Thread(target=recvMsg, args=(self.client_socket,))
        t2.start()

    def send(self, nk, ik):
        data = pickle.dumps((nk, ik))
        self.client_socket.sendall(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.run()
    sys.exit(app.exec_())

