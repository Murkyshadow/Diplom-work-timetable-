import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QLineEdit, QListView, QToolButton, QMainWindow)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QAbstractListModel, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidget

style_sheet = '''
QListView {
    background-color:white;
    font-size:16px;
    font-family:Comic Sans MS;
}
QListView::item:alternate {
    background:#f7f7f7;
}
QListView::item::hover {
    background: #0ff;
}
'''

class Timer():
    def __init__(self):  # таймер
        self.st = time.time()

    def end(self):
        return float("%.2f" % (time.time() - self.st))

class ListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._data = []
        self._checklist = []

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        row = index.row()
        if role == Qt.DisplayRole:
            return self._data[row]
        elif role == Qt.DecorationRole:
            return QIcon('Dark_rc/checkbox_checked.png') if self._checklist[row] else QIcon('Dark_rc/checkbox_unchecked.png')

    def flags(self, index):
        return Qt.ItemIsEnabled  # | Qt.ItemIsSelectable

    def load(self, lst):
        self.beginResetModel()
        self._data = lst
        self._checklist = [False] * len(lst)
        self.endResetModel()

    def get(self):
        return ', '.join(x for x, y in zip(self._data, self._checklist) if y)

class View(QListView):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("padding: 0px; margin: 0px;")
        # self.setWindowFlags(Qt.Popup)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.window = QDialog()
        self.setAlternatingRowColors(True)
        self.setStyleSheet(style_sheet)
        self.model = ListModel()
        self.setModel(self.model)

class PopupWidget(QWidget):
    state_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup)
        self.initView()
        self.view.clicked.connect(self.state_change)  # отслеживается клик по элементу
        self.time_for_open = Timer()

    def state_change(self, index):
        self.view.model._checklist[index.row()] ^= True
        self.view.model.layoutChanged.emit()
        self.state_changed.emit(self.view.model.get())

    def initView(self):
        self.view = View()
        self.view.setAlternatingRowColors(True)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(0)
        hbox.addWidget(self.view)

    def closeEvent(self, event):
        self.time_for_open = Timer()

class MyCheckableComboBox(QWidget):
    def __init__(self):
        super().__init__()
        self.line = QLineEdit()
        self.line.setReadOnly(True)
        self.btn = QToolButton()
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.btn.setIcon(QIcon('img_rc/array_down.png'))
        self.popup_win = PopupWidget()

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(0)
        hbox.addWidget(self.line)
        hbox.addWidget(self.btn)
        self.btn.clicked.connect(self.show_popup)
        self.popup_win.state_changed.connect(lambda x: self.line.setText(x))

    def addElements(self, elements):
        self.popup_win.view.model.load(elements)

    def show_popup(self):
        if not self.popup_win.isVisible() and self.popup_win.time_for_open.end() >= 0.4:    # если сейчас окно закрыто и с момента закрытия прошло 0.4 секунды
            self.popup_win.setGeometry(100, 200, 100, 100)
            self.popup_win.resize(self.width(), 90)
            self.popup_win.move(self.mapToGlobal(QPoint(0, self.height())))
            self.setFont(self.font())
            self.popup_win.show()

app = QApplication([])
win = QMainWindow()
w = MyCheckableComboBox()
win.setStyleSheet(style_sheet)
w.addElements(list('12345678'))
win.setCentralWidget(w)
win.show()

app.exec()