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


# q = QSqlQuery("select * FROM Teacher", con)
# modelForComboBox.setQuery(q)
# modelForComboBox.select()

# tableDel.setCellWidget(y, 0, btnDel)    # для TableWidget
# tableData.setIndexWidget(model.index(y, model.columnCount()-1), btnDel)

# model.index(row, column).data()

class DataBase():
    def __init__(self):
        self.con = sqlite3.connect('Timetable.db')
        cur = self.con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS Teacher
        (
          fullName TEXT,
          id INTEGER PRIMARY KEY AUTOINCREMENT
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS Lesson
        (
          title TEXT,
          hour INT,
          audienceNumber TEXT,
          teacherId INT,
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          FOREIGN KEY (teacherId) REFERENCES Teacher(id) ON DELETE SET NULL ON UPDATE CASCADE
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS GroupTimetable
        (
          dayOfWeek INT,
          weekNumber INT,
          lessonNumber INT,
          lessonId INT,
          FOREIGN KEY (lessonId) REFERENCES Lesson(id) ON DELETE SET NULL ON UPDATE CASCADE
        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Groups
        (
          title TEXT,
          courseNumber INT,
          PRIMARY KEY (title) 
        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS  TeacherAttendance
        (
          dayOfWeek INT,
          lessonNumber INT,
          weekNumber INT,
          teacherId INT,
          FOREIGN KEY (teacherId) REFERENCES Teacher(id) ON DELETE SET NULL ON UPDATE CASCADE
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS GroupLesson
        (
          lessonId INT,
          groupTitle TEXT,
          FOREIGN KEY (lessonId) REFERENCES Lesson(id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (groupTitle) REFERENCES Groups(title) ON DELETE CASCADE ON UPDATE CASCADE
        );""")
        cur.execute("""PRAGMA foreign_keys = ON;""")
        cur.close()

    def getTeacher(self):
        cur = self.con.cursor()
        cur.execute("""SELECT fullName, id FROM Teacher""")
        data = {}
        for rec in cur.fetchall():
            data[rec[1]] = rec[0]
        cur.close()
        return data

    def delRow(self, id, titleTable):
        cur = self.con.cursor()
        cur.execute(f"""DELETE FROM {titleTable} WHERE id = {id}""")
        self.con.commit()
        cur.close()


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.DB = DataBase()
        self.ui = PyQt5.uic.loadUi("main.ui")
        self.ui.show()
        setStyle(self.ui)
        self.tableWithDel(self.ui.tableTeacher, self.ui.btnAddTeacher, ['Учителя', 'id', ''], "Teacher")
        self.tableWithDel(self.ui.tableGroup, self.ui.btnAddGroup, ['Группы', 'Курс', ''], "Groups")
        self.tableWithDel(self.ui.tableLesson, self.ui.btnAddLesson, ['0', '1', '2', '3', '4', '5'], "Lesson")

    def tableWithDel(self, tableData, btnAdd, headTable, titleTable):
        def setWidgets(title=False):
            """
            после .select() нужно вставить виджеты и скрыть колонку id
            :param title: при первом заполнении таблицы так же нужно вставить заголовки
            :return:
            """
            model.insertColumn(model.columnCount())  # для удаления
            setBtnDel()
            if titleTable == "Teacher" or titleTable == "Lesson":
                tableData.setColumnHidden(model.columnCount() - 2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
            if titleTable == "Groups":
                setSpinBox()
            elif titleTable == "Lesson":
                setSpinBox(1, 99999)  # добавляем spinbox
                setComboBox(3, self.DB.getTeacher())
                setComboBox(3, self.DB.getTeacher())
            if title:
                for i, head in enumerate(headTable):
                    model.setHeaderData(i, Qt.Horizontal, head)
            changeTable()

        def setBtnAdd():
            """добавляем кнопку добавления новой строки"""
            def addRowTable():
                """добавление строки в таблицу при нажатии на кнопку"""
                model.submitAll()   # ячейка при добавлении новой может еще редактироваться пользователем, поэтому надо сначала принять введенное (при редактировании нельзя добавить)
                record = model.record()
                if titleTable == "Teacher":
                    record.remove(record.indexOf("id"))
                    record.setValue("fullName", "")
                elif titleTable == "Groups":
                    record.setValue("title", "")
                    record.setValue("courseNumber", 1)
                elif titleTable == "Lesson":
                    record.remove(record.indexOf("id"))
                    record.setValue("title", "")
                    record.setValue("hour", 1)
                    record.setValue("audienceNumber", 1)
                    record.setValue("teacherId", "")
                model.insertRecord(-1, record)
                model.submitAll()
                model.select()
                setWidgets()
                # if titleTable == "Groups":
                #     setSpinBox()
                # elif titleTable == "Lesson":
                #     setSpinBox(1, 99999)  # добавляем spinbox
                #     setComboBox(3, self.DB.getTeacher())
                #
                # model.insertColumn(model.columnCount())  # для удаления
                # if titleTable == "Teacher" or titleTable == "Lesson":
                #     tableData.setColumnHidden(model.columnCount() - 2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
                # setBtnDel()
                tableData.scrollToBottom()   # пролистываем вниз

            btnAdd.clicked.connect(addRowTable)
            btnAdd.setStyleSheet("""background-color: rgb(255,255,255); text-align: center;""")
            btnAdd.setMinimumSize(30, 30)
            i = QIcon("add.png")
            btnAdd.setIcon(QtGui.QIcon(i))

        def setBtnDel():
            """установка кнопок удаления в таблицу"""
            def delRowTable():
                """удаление строки из таблицы и бд при нажатии на кнопку"""
                btnDel = self.sender()
                row = tableData.indexAt(btnDel.pos()).row()
                # model.removeRow(row)
                self.DB.delRow(model.index(row, model.columnCount()-2).data(),titleTable)
                model.submitAll()
                model.select()
                setWidgets()

            row = model.rowCount()  # кол-во строк
            for y in range(row):
                btnDel = QPushButton()
                btnDel.setMaximumSize(48, 1000)
                btnDel.setStyleSheet("""background-color: rgb(255,255,255); text-align: center;""")
                i = QIcon("del.png")
                btnDel.setIcon(QtGui.QIcon(i))
                tableData.setIndexWidget(model.index(y, model.columnCount()-1), btnDel)
                btnDel.clicked.connect(lambda: delRowTable())

        def setSpinBox(column=1, max=5):
            @pyqtSlot()
            def setFromSpinBox():   # вызывается при установке значения из spinBox в БД
                model.submitAll()
                spinBox = self.sender()
                rowSpinBox = tableData.indexAt(spinBox.pos()).row()
                columnSpinBox = tableData.indexAt(spinBox.pos()).column()
                numForSet = spinBox.value() # вставляем число в бд
                record = model.record()
                for col in range(model.columnCount()-1):
                    record.setValue(col, model.index(rowSpinBox, col).data())
                    if col == columnSpinBox:
                        record.setValue(1, numForSet)
                model.updateRowInTable(rowSpinBox, record)

            for row in range(model.rowCount()):  # кол-во строк
                spinBox = QSpinBox()
                spinBox.setMaximum(max)
                spinBox.setMinimum(1)
                spinBox.setValue(model.index(row, column).data())   # вставляем в spinbox данные из ячейки
                tableData.setIndexWidget(model.index(row, column), spinBox)
                spinBox.editingFinished.connect(setFromSpinBox)

        def setComboBox32(column, data):
            def setFromComboBox32(data, comboBox = None, rowComboBox = 123, columnComboBox=123):
                """при изменении значении в combobox вставляет это значение в БД"""
                changeTable()
                model.submitAll()
                record = model.record()
                if comboBox is None:
                    comboBox = self.sender()
                    comboBox.setStyleSheet("""""")
                    rowComboBox = tableData.indexAt(comboBox.pos()).row()
                else:
                    comboBox.setStyleSheet("""background-color:rgb(255,128,138);""")
                nowTeacher = comboBox.currentText()


                for textForSet in list(data.items()):     # ищем id учителя, чтобы вставить его в бд
                    if nowTeacher in textForSet:
                        idNowTeacher = textForSet[0]
                        break
                print('ищем id в', list(data.items()))
                print('изменена в комбобоксе на', nowTeacher, idNowTeacher, 'позиция', comboBox, rowComboBox, columnComboBox)

                for col in range(model.columnCount() - 1):
                    record.setValue(col, model.index(rowComboBox, col).data())
                    if col == columnComboBox:
                        record.setValue(col, idNowTeacher)
                # for i in range(model.columnCount()):
                #     print(record.value(i), end=' ')
                # model.submitAll()
                model.updateRowInTable(rowComboBox, record)
                model.submitAll()

            dataForSet = list(data.values())
            print('вставляем в комбобокс', dataForSet)
            for row in range(model.rowCount()):
                comboBox = QComboBox()
                comboBox.addItems(dataForSet)
                tableData.setIndexWidget(model.index(row, column), comboBox)
                rowFalse = tableData.indexAt(comboBox.pos()).row()
                # print('строка', rowFalse, 'на самом деле -', row)
                print('позиция', comboBox, tableData.indexAt(comboBox.pos()).row(), tableData.indexAt(comboBox.pos()).column())
                idTeacher = model.index(row, column).data()     # берем текущее id учителя из таблицы
                if idTeacher != '':
                    nowTeacher = data[idTeacher]        # по id находим имя учителя
                    indTeacher = dataForSet.index(nowTeacher)
                    comboBox.setCurrentIndex(indTeacher)       # вставляем индекс текущее имя в comboBox
                    comboBox.currentIndexChanged.connect(lambda: setFromComboBox(data, columnComboBox=column))
                elif comboBox.currentText() != '':
                    print('пусто')
                    comboBox.currentIndexChanged.connect(lambda: setFromComboBox(data, columnComboBox=column))
                    setFromComboBox(data, comboBox, tableData.indexAt(comboBox.pos()).row(), columnComboBox=column)

        def setComboBox(column, data):
            """
            вставка QCombobox в таблицу
            :param column: колонка куда вставляется QComboBox
            :param data: данные для вставки {id:data}
            """
            def setFromComboBox():
                '''при изменении значении в combobox вставляем это значение в БД'''
                print('комбобокс изменен')
                comboBox = self.sender()
                comboBox.setStyleSheet("""""")
                rowComboBox = tableData.indexAt(comboBox.pos()).row()
                columnComboBox = tableData.indexAt(comboBox.pos()).column()
                id = int(comboBox.currentText().split('/')[1])
                updateRow(rowComboBox, columnComboBox, id)

            for row in range(model.rowCount()):
                comboBox = QComboBox()
                comboBox.addItems([v+' / '+str(k) for k, v in data.items()])
                nowId = model.index(row, column).data()  # берем из таблицы внешней ключ

                if nowId == '' and data:
                    updateRow(row, column, int(comboBox.currentText().split('/')[1]))
                    comboBox.setStyleSheet("""background-color:rgb(255,128,138);""")
                elif nowId != '':
                    comboBox.setCurrentText(data[nowId]+str(nowId))
                tableData.setIndexWidget(model.index(row, column), comboBox)
                comboBox.currentIndexChanged.connect(lambda: setFromComboBox())

        def updateRow(row, column, id):
            """
            обнавляем строку в таблице (при добавлении значения в бд из виджета)
            :param row:
            :param id:
            :return:
            """
            record = model.record()
            for col in range(model.columnCount() - 1):
                print(model.index(row, col).data())
                if col == column:
                    record.setValue(col, id)
                else:
                    record.setValue(col, model.index(row, col).data())
            model.updateRowInTable(row, record)

        def changeTable():
            """вызывается при изменении ячейки"""
            print('ячейка изменена')
            tableData.resizeColumnsToContents()
            tableData.horizontalHeader().setSectionResizeMode(model.columnCount() - 1, 9999999)
            model.submitAll()

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

            # setWidgets(model)
            # model.insertColumn(model.columnCount())    # для удаления
            # if titleTable == "Teacher" or titleTable == "Lesson":
            #     tableData.setColumnHidden(model.columnCount()-2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
            # # if titleTable == "Lesson":
            # #     model.insertColumn(model.columnCount()-1)    # для групп

            # for i, head in enumerate(headTable):
            #     model.setHeaderData(i, Qt.Horizontal, head)

            # tableData.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            # tableData.resizeRowsToContents()
            return model

        model = setTableData()
        setWidgets(True)
        # for i, head in enumerate(headTable):
        #     model.setHeaderData(i, Qt.Horizontal, head)
        # changeTable()
        model.dataChanged.connect(changeTable)
        setBtnAdd()
        # if titleTable == 'Lesson':
        #     self.ui.upd.clicked.connect(updateRow)

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

# class Widget(Qt.QWidget):
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
