from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QLineEdit, QListView, QToolButton)
from PyQt5.QtCore import Qt, QAbstractListModel, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QMainWindow


class View(QListView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)

    def focusOutEvent(self, e):
        e.accept()
        self.hide()


class myMenu(QWidget):
    def __init__(self, parent=None):
        super(myMenu, self).__init__(parent)
        self.btn = QToolButton(self)
        self.view = View()
        layout = QHBoxLayout(None)
        layout.addWidget(self.btn)
        self.setLayout(layout)
        self.btn.clicked.connect(self.open_menu)

    def open_menu(self):
        # QtCore.QTimer.singleShot(3000, lambda: self.view.hide())
        # предохранитель - вещь не лишняя, но может и отсутствовать
        self.view.show()
        self.view.setFocus()


app = QApplication([])
win = QMainWindow()

w = myMenu()
win.setCentralWidget(w)
win.show()
app.exec()