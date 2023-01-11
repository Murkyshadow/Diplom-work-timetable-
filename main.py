import sys

import PyQt5.uic
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from itertools import product
from PyQt5 import Qt
from PyQt5 import QtRemoteObjects

import sqlite3
from PyQt5.QtSql import *

from functools import partial # scrollbar
from PyQt5.QtCore import Qt

class DataBase():
    def __init__(self):
        con = sqlite3.connect('Timetable.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS Teacher
        (
          fullName INT NOT NULL,
          id INT NOT NULL,
          PRIMARY KEY (id)
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS Lesson
        (
          title INT NOT NULL,
          hour INT NOT NULL,
          id INT NOT NULL,
          audienceNumber INT NOT NULL,
          teacherId INT NOT NULL,
          PRIMARY KEY (id),
          FOREIGN KEY (teacherId) REFERENCES Teacher(id)
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS GroupTimetable
        (
          dayOfWeek INT NOT NULL,
          weekNumber INT NOT NULL,
          lessonNumber INT NOT NULL,
          lessonId INT NOT NULL,
          FOREIGN KEY (lessonId) REFERENCES Lesson(id)
        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Groups
        (
          title INT NOT NULL,
          courseNumber INT NOT NULL,
          PRIMARY KEY (title)
        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS  TeacherAttendance
        (
          dayOfWeek INT NOT NULL,
          lessonNumber INT NOT NULL,
          weekNumber INT NOT NULL,
          teacherId INT NOT NULL,
          FOREIGN KEY (teacherId) REFERENCES Teacher(id)
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS GroupLesson
        (
          lessonId INT NOT NULL,
          groupTitle INT NOT NULL,
          FOREIGN KEY (lessonId) REFERENCES Lesson(id),
          FOREIGN KEY (groupTitle) REFERENCES Groups(title)
        );""")

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.DB = DataBase()
        self.ui = PyQt5.uic.loadUi("main.ui")
        self.ui.show()
        setStyle(self.ui)
        self.tableWithDel(self.ui.tableTeacherDelete, self.ui.tableTeacher, self.ui.btnAddTeacher, ['Учитель', ''], "Teacher")
        self.tableWithDel(self.ui.tableGroupDelete, self.ui.tableGroup, self.ui.btnAddGroup, ['Группа', 'Курс', ''], "Groups")

    def tableWithDel(self, tableDel, tableData, btnAdd, headTable, titleTable):
        def addRowTable():
            """добавление строки в таблицу при нажатии на кнопку"""
            record = model.record()
            if titleTable == "Teacher":
                record.remove(record.indexOf("id"))
                record.setValue("fullName", "")
            elif titleTable == "Groups":
                record.setValue("title", "")
                record.setValue("courseNumber", 1)
            model.insertRecord(-1, record)
            model.select()
            # if 'Groups' == titleTable:
            #     model.insertColumn(len(headTable) - 1)
            # if titleTable == "Groups":
            #     addSpinBox()
            if titleTable == "Teacher":
                tableData.setColumnHidden(1, True)  # спрятать id для Teacher
            model.insertColumn(len(headTable) - 1)
            setBtnDel()
            tableData.scrollToBottom()   # пролистываем вниз

        def delRowTable():
            """удаление строки из таблицы и бд при нажатии на кнопку"""
            btn = self.sender()
            row = tableData.indexAt(btn.pos()).row()
            model.removeRow(row)
            model.select()
            if titleTable == "Teacher":
                tableData.setColumnHidden(1, True)  # спрятать id для Teacher
            model.insertColumn(len(headTable)-1)    # для удаления
            # if 'Groups' == titleTable:
            #     model.insertColumn(len(headTable) - 1)
            # print("нажата кнопка удаления", row, model)
            # print('кол-во строк и колонн', row, model.columnCount())  # кол-во строк
            setBtnDel()

        def setBtnDel():
            """установка кнопок удаления в таблицу"""
            row = model.rowCount()  # кол-во строк
            # tableDel.setColumnCount(1)
            # tableDel.setRowCount(row)
            # if titleTable == "Teacher":
            #     tableData.setColumnHidden(1, True)  # спрятать id для Teacher
            for y in range(row):
                btnDel = QPushButton()
                btnDel.setMaximumSize(48, 1000)
                btnDel.setStyleSheet("""background-color: rgb(255,255,255); text-align: center;""")
                i = QIcon("del.png")
                btnDel.setIcon(QtGui.QIcon(i))
                # tableDel.setCellWidget(y, 0, btnDel)    # для TableWidget
                tableData.setIndexWidget(model.index(y, len(headTable)-1), btnDel)
                # tableData.horizontalHeader().setSectionResizeMode(0, 1111)
                # tableData.horizontalHeader().setSectionResizeMode(1, 111)
                # tableData.horizontalHeader().setSectionResizeMode(2, 111)
                btnDel.clicked.connect(lambda: delRowTable())
            tableDel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        def addSpinBox():
            @pyqtSlot()
            def setFromSpinBox():   # вызывается при установке значения в spinBox
                print('цифорка')
                spinBox = self.sender()
                row = tableData.indexAt(spinBox.pos()).row()
                course = spinBox.value()
                record = model.record()
                record.setValue(0, model.index(row, 0).data())
                record.setValue(1, course)
                model.updateRowInTable(row, record)
                model.submitAll()

            print('вставляем spinBox')
            for row in range(model.rowCount()):  # кол-во строк
                spinBox = QSpinBox()
                spinBox.setValue(model.index(row, 1).data())
                tableData.setIndexWidget(model.index(row, 1), spinBox)
                spinBox.editingFinished.connect(setFromSpinBox)

        def setTableData():
            """установка данных в таблицу из БД """
            con = QSqlDatabase.addDatabase("QSQLITE")
            con.setDatabaseName('Timetable.db')
            con.open()

            model = QSqlTableModel()
            model.setTable(titleTable)
            model.select()

            tableData.setModel(model)
            tableData.verticalHeader().hide()   # спрятать цифры сбоку
            if titleTable == "Teacher":
                tableData.setColumnHidden(1, True)  # спрятать id для Teacher
            model.insertColumn(len(headTable)-1)    # для удаления

            for i, head in enumerate(headTable):
                model.setHeaderData(i, Qt.Horizontal, head)

            tableData.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            tableData.resizeColumnsToContents()
            tableData.resizeRowsToContents()
            return model

        # для удаления
        model = setTableData()
        # if titleTable == "Groups":
        #     addSpinBox()  # добавляем spinbox
        setBtnDel()

        btnAdd.clicked.connect(addRowTable)
        btnAdd.setStyleSheet("""background-color: rgb(255,255,255); text-align: center;""")
        i = QIcon("add.png")
        btnAdd.setIcon(QtGui.QIcon(i))

def setStyle(ui):
    ui.setStyleSheet("""
    QPushButton {background-color: rgb(255,0,0); text-align: center;}
    QLabel {background-color: rgb(255,128,0);}
    QWidget {font-size:16px; fon-family:Comic Sans MS;}
    """)

if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    window = MainWindow()

    qapp.exec()

class Widget(Qt.QWidget):
    # def __init__(self):
    #     super().__init__()
    #     layout = Qt.QHBoxLayout(self)
    #     table = Qt.QTableWidget()
    #     table.setRowCount(2)
    #     table.setColumnCount(2)
    #     self.buttons = {}
    #     for y in range(2):
    #         btn = Qt.QPushButton("x")
    #         self.buttons[btn] = y
    #         btn.setObjectName(f'button{y}')
    #         table.setCellWidget(y, 0, btn)
    #         btn.clicked.connect(lambda: self.out(table))
    #     layout.addWidget(table)
    #     print(table.indexAt(btn.pos()).row())
    #
    # def out(self, table):
    #     btn = self.sender()
    #     row = table.indexAt(btn.pos()).row()
    #     column = table.indexAt(btn.pos()).column()
    #     print(self.buttons[btn])

    def __init__(self):
        super().__init__()
        layout = Qt.QHBoxLayout(self)
        tab = QTableView()
        model = Qt.QStandardItemModel()
        model.setRowCount(2)
        model.setColumnCount(2)
        self.buttons = {}
        tab.setModel(model)

        for y in range(2):
            btn = Qt.QPushButton("x")
            self.buttons[btn] = y
            btn.setObjectName(f'button{y}')

            tab.setEditTriggers(QAbstractItemView.NoEditTriggers)
            tab.setIndexWidget(model.index(y, 0), QPushButton("button"))

            # table.setCellWidget(y, 0, btn)
            btn.clicked.connect(lambda: self.out(tab))

        layout.addWidget(tab)
        print(tab.indexAt(btn.pos()).row())

    def out(self, table):
        btn = self.sender()
        row = table.indexAt(btn.pos()).row()
        column = table.indexAt(btn.pos()).column()
        print(self.buttons[btn])


# if __name__ == '__main__':
#     app = Qt.QApplication([])
#     w = Widget()
#     w.show()
#     app.exec()

# import sys
# from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
#                              QApplication, QPushButton)
#
#
# class MainWindow(QMainWindow):
#     def __init__(self, x):                                         # x <-- 3
#         super().__init__()
#
#         self.centralwidget = QWidget()
#         self.setCentralWidget(self.centralwidget)
#         self.lay = QVBoxLayout(self.centralwidget)
#
#         for i in range(x):                                          # <---
#             self.btn = QPushButton('Button {}'.format(i +1), self)
#             text = self.btn.text()
#             self.btn.clicked.connect(lambda ch, text=text : print("\nclicked--> {}".format(text)))
#             self.lay.addWidget(self.btn)
#
#         self.numButton = 4
#
#         pybutton = QPushButton('Create a button', self)
#         pybutton.clicked.connect(self.clickMethod)
#
#         self.lay.addWidget(pybutton)
#         self.lay.addStretch(1)
#
#     def clickMethod(self):
#         newBtn = QPushButton('New Button{}'.format(self.numButton), self)
#         self.numButton += 1
#         newBtn.clicked.connect(lambda : print("\nclicked===>> {}".format(newBtn.text())))
#         self.lay.addWidget(newBtn)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mainWin = MainWindow(3)                                            # 3 --> x
#     mainWin.show()
#     sys.exit( app.exec_() )

# from PyQt5 import QtCore, QtGui, QtWidgets
#
# class WidgetGallery(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         super(WidgetGallery, self).__init__(parent)
#         self.table = QtWidgets.QTableWidget(10, 3)
#         col_1 = QtWidgets.QTableWidgetItem("first_col")
#         col_2 =QtWidgets.QTableWidgetItem("second_col")
#         deleteButton = QtWidgets.QPushButton("delete_this_row")
#         deleteButton.clicked.connect(self.deleteClicked)
#         self.table.setItem(0, 0, col_1)
#         self.table.setItem(0, 1, col_2)
#         self.table.setCellWidget(0, 2, deleteButton)
#         self.mainLayout = QtWidgets.QGridLayout(self)
#         self.mainLayout.addWidget(self.table)
#
#     @QtCore.pyqtSlot()
#     def deleteClicked(self):
#         button = self.sender()
#
#         if button:
#             row = self.table.indexAt(button.pos()).row()
#             self.table.removeRow(row)
#
# if __name__ == '__main__':
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     w = WidgetGallery()
#     w.show()
#     sys.exit(app.exec_())


# app = QtWidgets.QApplication([])
#
# # wordlist for testing
# wordlist = [''.join(combo) for combo in product('abc', repeat = 4)]
#
# combo = QtWidgets.QComboBox()
# combo.addItems(wordlist)
#
# # completers only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
# combo.setEditable(True)
# combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
#
# # change completion mode of the default completer from InlineCompletion to PopupCompletion
# combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
#
# combo.show()
# app.exec()
