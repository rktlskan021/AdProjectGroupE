import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QTime
class MyWindow(QWidget):
    time = QTime(0, 0, 10)
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout)
        self.setWindowTitle('타이머 아이템')
        self.setGeometry(100, 100, 400, 200)
        self.timer.start()

        layout = QVBoxLayout()

        self.lcd = QLCDNumber()
        self.lcd.display('')
        subLayout = QHBoxLayout()

        self.item2 = QPushButton("아이템2")
        self.item2.clicked.connect(self.ButtonClicked)

        layout.addWidget(self.lcd)

        subLayout.addWidget(self.item2)
        layout.addLayout(subLayout)
        self.setLayout(layout)

    def ButtonClicked(self):
        self.time = self.time.addSecs(5)
        self.item2.setEnabled(False)
    def timeout(self):
        if self.time.toString("mm:ss") == "00:00":
            self.timer.stop()
        time = self.time.toString("mm:ss")
        self.lcd.display(time)
        self.time = self.time.addSecs(-1)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())
