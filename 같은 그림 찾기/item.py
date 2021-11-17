import sys
import time
import threading

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton



class MyApp(QWidget):
    a = 0
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        item_button = QPushButton('아이템1', self)
        item_button.setGeometry(500, 250, 100, 100)
        item_button.clicked.connect(self.click)
        pic = QPushButton("", self)
        pic.setGeometry(200, 150, 300, 300)
        pic.setIcon(QtGui.QIcon('1234.png'))
        pic.setIconSize(QtCore.QSize(270, 270))
        pic.clicked.connect(self.pic_click)
        self.setWindowTitle('아이템')
        self.setGeometry(300, 300, 700, 700)
        self.show()

    def click(self):
        self.a = 1

    def pic_click(self):
        b = self.sender()
        if self.a == 1:
            self.a = 0
            b.setIcon(QtGui.QIcon('image/biking.png'))
            b.setIconSize(QtCore.QSize(270, 270))
            c = [b]
            t = threading.Thread(target=self.useItem, args=(c))
            t.start()

    def useItem(self, b):
        t = time.time()
        while time.time() - t <= 2:
            continue
        b.setIcon(QtGui.QIcon('1234.png'))
        b.setIconSize(QtCore.QSize(270, 270))

    def disable_but(self, vbutton):
        vbutton.setEnabled(False)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
