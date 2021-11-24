import sys, random
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLineEdit, QToolButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QLayout, QGridLayout, QPushButton, QLCDNumber
from PyQt5.QtCore import QTimer, Qt

current = 120
player_current = 3
imageList = ["image/dog1.jpg", "image/dog2.jpg", "image/dog3.jpg",
             "image/dog4.jpg", "image/cat1.jpg", "image/cat2.jpg",
             "image/cat3.jpg", "image/bare1.jpg"]

itemList = ["image/clock.jpg", "image/card.jpg"]

c = []
dic = {}

class Button(QToolButton):

    def __init__(self, icon, callback, index_0=None, index_1=None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setIcon(QtGui.QIcon(icon))
        self.setIconSize(QtCore.QSize(110, 110))
        self.clicked.connect(callback)
        if index_0 is None:
            pass
        else:
            pair[index_0][index_1] = self
            c.append(self)

    def sizeHint(self):
        size = super(Button, self).sizeHint()
        size.setHeight(size.height() + 20)
        size.setWidth(max(size.width(), size.height()))
        return size


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # 레이아웃 선언
        playerBox = QVBoxLayout()
        itemBox = QVBoxLayout()
        TimerBox = QVBoxLayout()
        GameBox = QGridLayout()
        middleBox = QHBoxLayout()
        mainBox = QVBoxLayout()

        # player text 상자 생성
        self.display = QLineEdit("it's your turn")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setMaxLength(15)

        # 타이머 생성
        self.timer = QTimer(self)
        self.lcd = QLCDNumber()
        self.StartButton = QPushButton("준비")
        self.Timer(self.timer, self.lcd, self.StartButton, self.countdown, self.StartButtonClicked)

        # player 타이머 생성
        self.player_timer = QTimer(self)
        self.player_lcd = QLCDNumber()
        self.player_StartButton = QPushButton("준비")
        self.Timer(self.player_timer, self.player_lcd, self.player_StartButton, self.player_countdown,
                   self.player_StartButtonClicked)

        # 아이템 버튼 생성
        for i in itemList:
            button = Button(i, self.itemClicked)
            itemBox.addWidget(button)

        # 카드 버튼 생성
        for i in imageList:
            for u in range(2):
                button = Button("image/human1.jpg", self.buttonClicked, imageList.index(i), u)
                dic[button] = i
        print(pair)
        random.shuffle(c)
        r = 0;
        d = 0
        for i in c:
            GameBox.addWidget(i, r, d)
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

        mainBox.addLayout(middleBox)
        mainBox.addStretch(1)
        mainBox.addLayout(GameBox)

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
        self.lcd.display(current)
        current -= 1
        if current < 0:
            self.lcd.display("00")
            self.timer.stop()

    def player_countdown(self):
        global player_current
        self.player_lcd.display(player_current)
        player_current -= 1
        if player_current < 0:
            self.player_lcd.display("00")
            self.player_timer.stop()

    def center(self):
        W_size = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        W_size.moveCenter(center)
        self.move(W_size.topLeft())

    def buttonClicked(self):
        key = self.sender()
        self.sender().setIcon(QtGui.QIcon(dic[key]))
        self.sender().setIconSize(QtCore.QSize(110, 110))

    def itemClicked(self):
        pass

    def Timer(self, timer, lcd, StartButton, callback1, callback2):
        timer.setInterval(1000)
        timer.timeout.connect(callback1)
        lcd.display("")
        lcd.setDigitCount(10)
        StartButton.clicked.connect(callback2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    sys.exit(app.exec_())