from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QLineEdit, QListView, QToolButton)
from PyQt5.QtCore import Qt, QAbstractListModel, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidget

style_sheet = '''
QListView {
    background-color:white;
}
QListView::item:alternate {
    background:#f7f7f7;
} 
QListView::item::hover {
    background: #0ff;
}
'''


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
            if self._checklist[row]:
                return QIcon('Dark_rc/checkbox_checked.png')
            else:
                return QIcon('Dark_rc/checkbox_unchecked.png')

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
        # self.setStyleSheet("padding: 0px; margin: 0px;")
        # self.setWindowFlags(Qt.Popup)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.window = QDialog()
        # self.setAlternatingRowColors(True)
        # self.setStyleSheet(style_sheet)
        self.model = ListModel()
        self.setModel(self.model)
        self.model.load(list('qwerty'))
        print('123')

        # self.clicked.connect(self.state_change)  # отслеживается клик по элементу

    # def state_change(self, index):
    #     self.model._checklist[index.row()] ^= True
    #     self.model.layoutChanged.emit()
    #     self.state_changed.emit(self.model.get())


class examplePopup(QWidget):
    state_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup)
        self.initUI()
        self.lblName.clicked.connect(self.state_change)  # отслеживается клик по элементу

    def state_change(self, index):
        print(index)
        self.lblName.model()._checklist[index.row()] ^= True
        self.lblName.model().layoutChanged.emit()
        self.state_changed.emit(self.lblName.model().get())

    def initUI(self):
        self.lblName = View()
        # self.lblName.setAlternatingRowColors(True)
        # self.model = ListModel()
        # self.lblName.setModel(self.model)
        # self.lblName.model.load((list('qwerty')))

class mComboBox(QWidget):
    def __init__(self):
        super().__init__()
        self.line = QLineEdit()
        self.line.setReadOnly(True)
        self.btn = QToolButton()
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.btn.setIcon(QIcon('img_rc/array_down.png'))
        self.exPopup = examplePopup()
        self.setWindowFlags(Qt.Popup)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(0)
        hbox.addWidget(self.line)
        hbox.addWidget(self.btn)
        self.btn.clicked.connect(self.on_popup)
        # self.exPopup.state_changed.connect(lambda x: self.line.setText(x))

    def on_popup(self):
        if self.exPopup.isVisible():
            self.exPopup.hide()
        else:
            self.exPopup.setGeometry(100, 200, 100, 100)
            self.exPopup.resize(self.width(), 90)
            self.exPopup.move(self.mapToGlobal(QPoint(0,self.height())))
            self.setFont(self.font())
            self.exPopup.show()

app = QApplication([])
w = mComboBox()

# w.setFont(QFont('times', 16))
w.exPopup.lblName.model.load(list('qwerty'))
w.show()
app.exec()