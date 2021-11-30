import sys
import socket
import threading
import pickle
import time

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget, QMessageBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLineEdit, QToolButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QLayout, QGridLayout, QPushButton, QLCDNumber
from PyQt5.QtCore import QTimer, Qt, QCoreApplication

current = 9999999
player_current = 9999999
# imageList = ["image/dog1.jpg", "image/dog2.jpg", "image/dog3.jpg",
#              "image/dog4.jpg", "image/cat1.jpg", "image/cat2.jpg",
#              "image/cat3.jpg", "image/bare1.jpg"]
imageList = []
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
    ip = 'localhost'
    port = 6000
    score = 0
    # outCount = 0
    turn = False
    clear = 0
    item2Use = False

    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((Game.ip, Game.port))
        self.run()
        self.initUI()
        self.findImageList = []

    def initUI(self):
        # 레이아웃 선언
        self.GameBox = QGridLayout()
        playerBox = QVBoxLayout()
        itemBox = QVBoxLayout()
        TimerBox = QVBoxLayout()
        middleBox = QHBoxLayout()
        self.mainBox = QVBoxLayout()

        # player text 상자 생성
        self.display = QLineEdit("Not Ready")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setMaxLength(15)

        # 타이머 생성
        self.timer = QTimer(self)
        self.lcd = QLCDNumber()
        self.StartButton = QPushButton("준비")
        self.Timer(self.timer, self.lcd, self.StartButton, self.countdown, self.StartButtonClicked)
        self.timer.start()

        # player 타이머 생성
        self.player_timer = QTimer(self)
        self.player_lcd = QLCDNumber()
        self.player_StartButton = QPushButton("준비")
        self.Timer(self.player_timer, self.player_lcd, self.player_StartButton, self.player_countdown,
                   self.player_StartButtonClicked)
        self.player_timer.start()

        # 아이템 버튼 생성
        button = Button("image/clock.jpg", self.item1Clicked)
        itemBox.addWidget(button)

        button = Button("image/card.jpg", self.item2Clicked)
        itemBox.addWidget(button)

        # 카드 버튼 생성
        for i in imageList:
            button = Button("image/human1.jpg", self.buttonClicked, imageList.index(i))
            dic[button] = (i, "image/human1.jpg")

        r = 0;d = 0
        for i in c:
            self.GameBox.addWidget(i, r, d)
            d += 1
            if d >= 4:
                d = 0
                r += 1

        # 레이아웃
        playerBox.addWidget(self.display)
        playerBox.addWidget(self.player_lcd)
        playerBox.addWidget(self.player_StartButton)

        TimerBox.addWidget(self.lcd)
        TimerBox.addWidget(self.StartButton)

        middleBox.addLayout(playerBox)
        middleBox.addStretch(1)
        middleBox.addLayout(TimerBox)
        middleBox.addStretch(1)
        middleBox.addLayout(itemBox)

        self.mainBox.addLayout(middleBox)
        self.mainBox.addStretch(1)
        self.mainBox.addLayout(self.GameBox)

        self.resize(1000, 900)
        self.setWindowTitle('Client')
        self.center()
        self.setLayout(self.mainBox)
        self.show()


    def StartButtonClicked(self):
        self.send('D', 1)
        self.display.setText("Ready")
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

    def player_countdown(self):
        global player_current
        if player_current <= 13:
            self.player_lcd.display(player_current)
        player_current -= 1
        if player_current < 0:
            self.player_lcd.display("00")
            player_current = 999999
            Game.turn = False
            self.setDisplay()
            self.reverseImage()
            t = threading.Thread(target=self.turnChange, args=())
            t.start()

    def center(self):
        W_size = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        W_size.moveCenter(center)
        self.move(W_size.topLeft())

    def item1Clicked(self):
        if Game.turn:
            global player_current
            player_current += 5
            self.sender().setEnabled(False)

    def item2Clicked(self):
        if Game.turn:
            Game.item2Use = True
            self.sender().setEnabled(False)

    def Timer(self, timer, lcd, StartButton, callback1, callback2):
        timer.setInterval(1000)
        timer.timeout.connect(callback1)
        lcd.display("")
        lcd.setDigitCount(10)
        StartButton.clicked.connect(callback2)

    # def startTimers(self):
    #     self.timer.start()

    def startPlayerTimer(self):
        self.player_timer.start()

    def buttonClicked(self):
        key = self.sender()
        if Game.turn and not Game.item2Use:
            imageKey = imageB[c.index(key)] = not imageB[c.index(key)]
            # self.sender().setIcon(QtGui.QIcon(dic[key][imageKey]))
            self.sender().setIconSize(QtCore.QSize(110, 110))
            self.send(c.index(key), imageKey)
            self.changeImage((c.index(key), imageKey))
        elif Game.item2Use:
            key.setIconSize(QtCore.QSize(110, 110))
            key.setIcon(QtGui.QIcon(dic[c[c.index(key)]][not imageB[c.index(key)]]))
            t = threading.Thread(target=self.coolTime, args=[2])
            t.start()

    def changeImage(self, info):
        key = info[0]
        imageKey = info[1]

        if key not in self.findImageList:
            self.findImageList.append(key)
        else:
            self.findImageList.remove(key)

        self.GameBox.itemAt(key).widget().setIcon(QtGui.QIcon(dic[c[key]][imageKey]))
        self.findImage()

    def findImage(self):
        if len(self.findImageList) == 2:
            firstItem = self.GameBox.itemAt(self.findImageList[0]).widget()
            secondItem = self.GameBox.itemAt(self.findImageList[1]).widget()
            if imageList[self.findImageList[0]] == imageList[self.findImageList[1]]:
                firstItem.setEnabled(False)
                secondItem.setEnabled(False)
                self.findImageList.clear()
                Game.clear += 1
                print(Game.clear)
                # 점수 추가
                if Game.turn:
                    self.score += 1
                    self.outCount = 0
                if Game.clear == 8:
                    self.send('E', ("client", self.score))
            else:
                # 실패 코드
                firstImage = not imageB[self.findImageList[0]]
                secondImage = not imageB[self.findImageList[1]]
                if Game.turn:
                    self.send('B', ((self.findImageList[0], self.findImageList[1]), (firstImage, secondImage)))
                self.reverse((self.findImageList[0], self.findImageList[1]), (firstImage, secondImage))
                self.findImageList.clear()
                # if self.outCount == 3 and Game.turn:
                #     # 턴 넘김
                #     Game.turn = False
                #     self.setDisplay()
                #     print("턴 넘김")
                #     self.outCount = 0
                #     t = threading.Thread(target=self.turnChange, args=())
                #     t.start()

    def reverseImage(self):
        for j, i in enumerate(c):
            if i.isEnabled():
                i.setIcon(QtGui.QIcon("image/human1.jpg"))
            imageB[j] = True
        self.findImageList.clear()

    def showImage(self):
        for j, i in enumerate(c):
            i.setIcon(QtGui.QIcon(imageList[j]))
        t = threading.Thread(target=self.coolTime, args=[3])
        t.start()

    def coolTime(self, c):
        global current
        t = time.time()
        while time.time() - t < c:
            continue
        if not Game.item2Use:
            current = 120
            Game.turn = True
            self.setDisplay()
        self.reverseImage()

    def turnChange(self):
        t = time.time()
        while(time.time() - t < 1):
            continue
        self.send('C', True)

    def reverse(self, first, second):
        imageB[first[0]] = second[0]
        imageB[first[1]] = second[1]
        firstItem = self.GameBox.itemAt(first[0]).widget()
        secondItem = self.GameBox.itemAt(first[1]).widget()
        firstItem.setIcon(QtGui.QIcon(dic[c[first[0]]][second[0]]))
        secondItem.setIcon(QtGui.QIcon(dic[c[first[1]]][second[1]]))

    def setDisplay(self):
        global player_current
        if Game.turn:
            self.display.setText("Your Turn")
            player_current = 8
        else:
            self.display.setText("Not Your Turn")
            player_current = 999999

    def run(self):
        t2 = threading.Thread(target=self.recvMsg, args=(self.client_socket,))
        t2.start()

    def send(self, nk, ik):
        print(f"({nk}, {ik})")
        try:
            self.client_socket.sendall(pickle.dumps((nk, ik)))
        except Exception as e:
            print(e)

    def recvMsg(self, soc):
        global imageList
        global current
        global player_current
        while True:
            data = soc.recv(1024)
            try:
                msg = pickle.loads(data)
            except:
                msg = data.decode()
            try:
                if msg[0] == 'A':
                    imageList = msg[1]
                elif msg[0] == 'B':
                    self.reverse(msg[1][0], msg[1][1])
                elif msg[0] == 'C':
                    self.reverseImage()
                    Game.turn = msg[1]
                    self.setDisplay()
                elif msg[0] == 'D':
                    self.showImage()
                else:
                    self.changeImage(msg)
            except KeyError:
                buttonReply = QMessageBox.question(self, "결과", f"Your score : {msg['client']}, Competitor score : {msg['client2']}", QMessageBox.Ok)
                if buttonReply == QMessageBox.Ok:
                    break
        soc.close()
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    sys.exit(app.exec_())