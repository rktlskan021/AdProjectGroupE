import sys
import socket
import threading
import time
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QToolButton, QSizePolicy)
from PyQt5 import QtGui
from image import imageList, imageB, imageChange

import pickle

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

# def sendMsg(soc):
#     while True:
#         msg = input('')
#         soc.sendall(msg.encode(encoding='utf-8'))
#         if msg != '':
#
#             break
#     print('id 입력 완료')


class Client(QWidget):
    ip = 'localhost'
    port = 5000
    score = 0
    outCount = 0

    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((Client.ip, Client.port))
        self.findImageList = []

    def initUI(self):
        # self.player1 = QLabel('player1')
        # self.player2 = QLabel('player2')

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
        self.setWindowTitle('Client')
        self.show()

    def buttonClicked(self):
        key = self.sender()
        numberKey = self.imageLayout.indexOf(key)
        imageKey = imageB[numberKey] = not imageB[numberKey]
        self.changeImage((numberKey, imageKey))
        # self.sender().setIcon(QtGui.QIcon(imageChange[numberKey][imageKey]))
        self.send(numberKey, imageKey)

    def run(self):
        # t = threading.Thread(target=sendMsg, args=(self.client_socket,))
        # t.start()
        t2 = threading.Thread(target=self.recvMsg, args=(self.client_socket,))
        t2.start()

    def send(self, nk, ik):
        data = pickle.dumps((nk, ik))
        self.client_socket.sendall(data)

    def recvMsg(self, soc):
        while True:
            data = soc.recv(1024)
            try:
                msg = pickle.loads(data)
            except:
                msg = data.decode()
            self.changeImage(msg)
            if msg == '/stop':
                break
        soc.close()
        print('클라이언트 리시브 쓰레드 종료')

    def changeImage(self, info):
        if info[0] in self.findImageList:
            self.findImageList.remove(info[0])
        else:
            self.findImageList.append(info[0])
        numberKey = info[0]
        imageKey = info[1]
        self.imageLayout.itemAt(numberKey).widget().setIcon(QtGui.QIcon(imageChange[numberKey][imageKey]))
        self.findImage()

    def findImage(self):
        if len(self.findImageList) == 2:
            firstItem = self.imageLayout.itemAt(self.findImageList[0]).widget()
            secondItem = self.imageLayout.itemAt(self.findImageList[1]).widget()
            if firstItem.objectName() == secondItem.objectName():
                firstItem.setEnabled(False)
                secondItem.setEnabled(False)
                self.findImageList.clear()
                # 점수 추가
                self.score += 1
            else:
                # 실패 코드
                firstNumber = self.imageLayout.indexOf(firstItem)
                secondNumber = self.imageLayout.indexOf(secondItem)
                firstImage = imageB[firstNumber] = not imageB[firstNumber]
                secondImage = imageB[secondNumber] = not imageB[secondNumber]
                firstItem.setIcon(QtGui.QIcon(imageChange[firstNumber][firstImage]))
                secondItem.setIcon(QtGui.QIcon(imageChange[secondNumber][secondImage]))
                self.findImageList.clear()
                self.outCount += 1
                if self.outCount == 3:
                    # 턴 넘김
                    print("턴 넘김")
                    self.outCount = 0



# 쿨타임 구현
# def coolTime():
#     t = threading.Thread(target=run, args=())
#     t.start()
#
# def run():
#     t = time.time()
#     while time.time() - t < 0.5:
#         continue

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.run()
    sys.exit(app.exec_())

