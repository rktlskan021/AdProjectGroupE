import sys, random
import socket
import threading
import pickle

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLineEdit, QToolButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QLayout, QGridLayout, QPushButton, QLCDNumber
from PyQt5.QtCore import QTimer, Qt

ip = ''
port = 6000
current = 999999
player_current = 3
imageList = ["image/dog1.jpg", "image/dog2.jpg", "image/dog3.jpg",
             "image/dog4.jpg", "image/cat1.jpg", "image/cat2.jpg",
             "image/cat3.jpg", "image/bare1.jpg",
             "image/dog1.jpg", "image/dog2.jpg", "image/dog3.jpg",
             "image/dog4.jpg", "image/cat1.jpg", "image/cat2.jpg",
             "image/cat3.jpg", "image/bare1.jpg"
             ]

itemList = ["image/clock.jpg", "image/card.jpg"]

imageB = [True for i in range(16)]
c = []
dic = {}

class Button(QToolButton):

    def __init__(self, icon, callback, index_0=None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setIcon(QtGui.QIcon(icon))
        self.setIconSize(QtCore.QSize(110, 110))
        self.clicked.connect(callback)
        if index_0 is None:
            pass
        else:
            c.append(self)

    def sizeHint(self):
        size = super(Button, self).sizeHint()
        size.setHeight(size.height() + 20)
        size.setWidth(max(size.width(), size.height()))
        return size


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.gamePlayer = []
        self.s = Server(self)
        self.startServer()
        self.initUI()

    def initUI(self):
        random.shuffle(imageList)

        # 레이아웃 선언
        self.GameBox = QGridLayout()
        playerBox = QVBoxLayout()
        itemBox = QVBoxLayout()
        TimerBox = QVBoxLayout()
        middleBox = QHBoxLayout()
        mainBox = QVBoxLayout()

        # 타이머 생성
        self.timer = QTimer(self)
        self.lcd = QLCDNumber()
        self.Timer(self.timer, self.lcd, self.countdown)
        self.timer.start()

        # 카드 버튼 생성
        for i in imageList:
            button = Button(i, self.buttonClicked, imageList.index(i))
            dic[button] = (i, "image/human1.jpg")

        r = 0;d = 0
        for i in c:
            self.GameBox.addWidget(i, r, d)
            d += 1
            if d >= 4:
                d = 0
                r += 1

        TimerBox.addWidget(self.lcd)

        middleBox.addLayout(playerBox)
        middleBox.addStretch(1)

        middleBox.addLayout(TimerBox)
        middleBox.addStretch(1)
        middleBox.addLayout(itemBox)

        mainBox.addLayout(middleBox)
        mainBox.addStretch(1)
        mainBox.addLayout(self.GameBox)

        self.setWindowTitle('Server')
        self.resize(1000, 900)
        self.center()
        self.setLayout(mainBox)
        self.show()

    def StartButtonClicked(self):
        self.timer.start()
        self.StartButton.setEnabled(False)

    def player_StartButtonClicked(self):
        self.player_timer.start()
        self.player_StartButton.setEnabled(False)

    def countdown(self):
        global current
        if current <= 120:
            self.lcd.display(current)
        current -= 1
        if current < 0:
            self.lcd.display("00")
            self.timer.stop()

    # def player_countdown(self):
    #     global player_current
    #     self.player_lcd.display(player_current)
    #     player_current -= 1
    #     if player_current < 0:
    #         self.player_lcd.display("00")
    #         self.player_timer.stop()

    def center(self):
        W_size = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        W_size.moveCenter(center)
        self.move(W_size.topLeft())

    def buttonClicked(self):
        key = self.sender()
        imageKey = imageB[c.index(key)] = not imageB[c.index(key)]
        self.sender().setIcon(QtGui.QIcon(dic[key][imageKey]))
        self.sender().setIconSize(QtCore.QSize(110, 110))

    def changeImage(self, info, soc):
        key = info[0]
        imageKey = info[1]
        self.GameBox.itemAt(key).widget().setIcon(QtGui.QIcon(dic[c[key]][imageKey]))
        self.send(info, soc)

    def Timer(self, timer, lcd, callback1):
        timer.setInterval(1000)
        timer.timeout.connect(callback1)
        lcd.display("")
        lcd.setDigitCount(10)

    def startServer(self):
        self.s.open()

    def addPlayer(self, c):
        self.gamePlayer.append(c)
        cc = Client(c, self)
        cc.run()

    def send(self, msg, soc):
        try:
            data = pickle.dumps(msg)
        except:
            data = msg.decode()

        for i in self.gamePlayer:
            try:
                if i != soc and msg[0] != 'D':
                    print("전송")
                    i.sendall(data)
                elif msg[0] == 'D':
                    i.sendall(data)
            except KeyError:
                i.sendall(data)

    def delClient(self, cli):
        cli.close()
        self.gamePlayer.remove(cli)

class Client:
    gameStart = 0
    gameScore = {}
    def __init__(self, soc, r):
        self.soc = soc
        self.r = r
    def recvs(self):
        global current
        while True:
            data = self.soc.recv(1024)
            try:
                msg = pickle.loads(data)
            except:
                msg = data.decode()

            if msg[0] == 'B':
                self.r.send(msg, self.soc)
            elif msg[0] == 'C':
                self.r.send(msg, self.soc)
            elif msg[0] == 'D':
                Client.gameStart += msg[1]
                if Client.gameStart == 2:
                    current = 120
                    self.r.send(msg, self.soc)
            elif msg[0] == 'E':
                Client.gameScore[msg[1][0]] = msg[1][1]
                if len(Client.gameScore) == 2:
                    self.r.send(Client.gameScore, self.soc)
                    break
            else:
                self.r.changeImage(msg, self.soc)

        self.r.delClient(self.soc)
        return

    def run(self):
        t = threading.Thread(target=self.recvs, args=())
        t.start()

class Server:
    def __init__(self, ui):
        self.server_socket = None
        self.ui = ui

    def open(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socket.setsockopt(self.server_socket, socket.SOL_SOCKET, socket.SO_REUSEADDR, 1, )
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.t = threading.Thread(target=self.listen, args=())
        self.t.start()

    def listen(self):
        print("서버시작")
        while True:
            self.server_socket.listen(2)
            client, addr = self.server_socket.accept()
            client.sendall(pickle.dumps(('A', imageList)))
            print(addr)
            self.ui.addPlayer(client)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    sys.exit(app.exec_())