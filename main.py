import sys
import typing

import PyQt5
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import *
from itertools import product
from PyQt5 import Qt
from PyQt5 import QtRemoteObjects

import sqlite3
from PyQt5.QtSql import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView

# from PyQt5.QtCore import Qt
# q = QSqlQuery("select * FROM Teacher", con)
# modelForComboBox.setQuery(q)
# modelForComboBox.select()

# tableDel.setCellWidget(y, 0, btnDel)    # для TableWidget
# tableData.setIndexWidget(model.index(y, model.columnCount()-1), btnDel)

# model.index(row, column).data()

# new check-able combo box


class CheckableComboBox3(QComboBox):

    # constructor
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))


    count = 0

    # action called when item get checked
    def do_action(self):
        print(self.count, 'action')
        # window.label.setText("Checked number : " + str(self.count))

    # when any item get pressed
    def handleItemPressed(self, index):
        print('handle', index)
        # getting the item
        item = self.model().itemFromIndex(index)

        # checking if item is checked
        if item.checkState() == Qt.Checked:

            # making it unchecked
            item.setCheckState(Qt.Unchecked)

        # if not checked
        else:
            # making the item checked
            item.setCheckState(Qt.Checked)

            self.count += 1

            # call the action
            self.do_action()

class CheckableComboBox2(QtWidgets.QComboBox):
    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, text):
        super(CheckableComboBox, self).addItem(text)
        print(QtCore.Qt.ItemFlag)
        item = self.model().item(self.count()-1,0)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.view().pressed.connect(self.action)

    def action(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            print('uncheck ', end='')
        else:
            print('check ', end='')
            item.setCheckState(QtCore.Qt.Checked)
        print('нажато', index)

    def itemChecked(self, index):
        print('12')
        item = self.model().item(i,0)
        return item.checkState() == QtCore.Qt.Checked

class MyCheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # self.closeOnLineEditClick = False
        print(self.model())
        self.model().dataChanged.connect(self.updateCheck)
        self.addItems('abcde')
        self.lineEdit().setText('Выберите что-то')
        self.view().pressed.connect(self.action)
        self.setStyleSheet(self.getStyle())

    def getStyle(self):
        return """
                :indicator:unchecked
                {
                    image: url(Dark_rc/checkbox_unchecked.png);
                }
                :indicator:checked
                {
                    image: url(Dark_rc/checkbox_checked.png);
                }
               """

    def action(self, index):    # при нажатии на текст
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def addItem(self, text, userData=None):
        item = QStandardItem()
        item.setText(text)
        if userData is None:
            item.setData(userData)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, items: typing.Iterable[str]) -> None:  # зачем None?
        for item in items:
            self.addItem(item)

    def itemChecked(self, index):
        item = self.model().item(index, 0)
        print(index, item.checkState())
        return item.checkState() == QtCore.Qt.Checked

    def updateCheck(self, index):
        # PyQt5.QtCore.QModelIndex.row()
        row = index.row()
        if self.model().item(row).checkState() == Qt.Checked:
            print('выбрано', self.model().item(row).text())
        elif self.model().item(row).checkState() == Qt.Unchecked:
            print('не выбрано', self.model().item(row).text())

        textChecked = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                textChecked.append(self.model().item(i).text())
        self.lineEdit().setText(', '.join(textChecked))

class DataBase():
    def __init__(self):
        self.con = sqlite3.connect('Timetable.db')
        cur = self.con.cursor()

        cur.execute("""PRAGMA foreign_keys = ON;""")
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
        cur.close()

    def getTeacher(self):
        cur = self.con.cursor()
        cur.execute("""SELECT fullName, id FROM Teacher""")
        data = {}
        for rec in cur.fetchall():
            data[rec[1]] = rec[0]
        cur.close()
        return data

    def getTitleTable(self, titleTable, titlePKColumn):
        self.con.row_factory = sqlite3.Row
        cursor = self.con.execute(f'select * from {titleTable}')
        row = cursor.fetchone()
        names = row.keys()
        return names.index(titlePKColumn)

    def delRow(self, id, titleTable, titlePKColumn):
        cur = self.con.cursor()
        cur.execute(f"""DELETE FROM {titleTable} WHERE {titlePKColumn} = '{id}'""")
        self.con.commit()
        cur.close()

class table(QtWidgets.QWidget):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QGridLayout()

        self.setLayout(self.layout)

        self.tableData = QtWidgets.QTableView()
        self.layout.addWidget(self.tableData)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('Timetable.db')
        con.open()

        model = QSqlTableModel()
        model.setTable('Teacher')
        model.select()
        self.tableData.setModel(model)

        self.tableData.setTextElideMode(Qt.ElideNone)
        self.tableData.horizontalHeader().setStretchLastSection(True)
        self.tableData.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableData.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # model.dataChanged.connect(self.changeTable)
        # self.tableData.horizontalHeader().setStretchLastSection(True)
        # self.tableData.resizeColumnToContents(0)


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setFont(QFont("Comic Sans", 16))
        self.DB = DataBase()
        self.ui = PyQt5.uic.loadUi("main.ui")
        setStyle(self.ui)
        self.ui.show()
        # self.clickBtnAdd = False

        teacher = tableWithDel(['Учителя', 'id', ''], "Teacher", 'id', self.DB)
        self.ui.horizontalLayout.addWidget(teacher)
        group = tableWithDel(['Группы', 'Курс', ''], "Groups", 'title', self.DB)
        self.ui.horizontalLayout_2.addWidget(group)
        lesson = tableWithDel(['Занятие', 'Часы', 'Кабинет', 'Учитель', 'id', ''], "Lesson", 'id', self.DB, self.ui.tabWidget)
        self.ui.horizontalLayout_3.addWidget(lesson)


class tableWithDel(QtWidgets.QWidget):
    def __init__(self, headTable, titleTable, titlePKColumn, DB, tabWidget=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QGridLayout()
        self.titlePKColumn = titlePKColumn  # для удаления столбца

        self.setLayout(self.layout)

        self.titleTable = titleTable
        self.tableData = QtWidgets.QTableView()
        self.layout.addWidget(self.tableData)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('Timetable.db')
        con.open()

        model = QSqlTableModel()
        model.setTable(self.titleTable)
        model.select()
        self.model = model
        self.tableData.setModel(model)
        self.model = self.setTableData()

        self.headTable = headTable
        self.DB = DB
        self.clickBtnAdd = False

        self.setBtnAdd()
        self.setWidgets(title=True)
        self.model.dataChanged.connect(self.changeTable)
        # self.changeTable()
        if tabWidget:
            tabWidget.currentChanged.connect(self.changeTab)
            self.tabWidget = tabWidget
        # self.tableData.setTextElideMode(Qt.ElideNone)
        self.tableData.horizontalHeader().setStretchLastSection(True)
        self.tableData.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableData.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def setWidgets(self, title=False):
        """
        после .select() нужно вставить виджеты и скрыть колонку id
        :param title: при первом заполнении таблицы так же нужно вставить заголовки
        :return:
        """
        self.model.insertColumn(self.model.columnCount())  # для удаления

        self.setBtnDel()
        if self.titleTable == "Teacher" or self.titleTable == "Lesson":
            self.tableData.setColumnHidden(self.model.columnCount() - 2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
        if self.titleTable == "Groups":
            self.setSpinBox()
        elif self.titleTable == "Lesson":
            self.setSpinBox(1, 99999)  # добавляем spinbox
            self.setComboBox(3, self.DB.getTeacher())
        if title:
            for i, head in enumerate(self.headTable):
                self.model.setHeaderData(i, Qt.Horizontal, head)
        self.changeTable()

    def addRowTable(self):
        """добавление строки в таблицу при нажатии на кнопку"""
        print('123')
        self.clickBtnAdd = True
        self.model.submitAll()   # ячейка при добавлении новой может еще редактироваться пользователем, поэтому надо сначала принять введенное (при редактировании нельзя добавить)
        record = self.model.record()
        if self.titleTable == "Teacher":
            record.remove(record.indexOf("id"))
            record.setValue("fullName", "")
        elif self.titleTable == "Groups":
            record.setValue("title", "")
            record.setValue("courseNumber", 1)
        elif self.titleTable == "Lesson":
            record.remove(record.indexOf("id"))
            record.setValue("title", "")
            record.setValue("hour", 1)
            record.setValue("audienceNumber", 1)
            record.setValue("teacherId", "")
        self.model.insertRecord(-1, record)
        # self.model.submitAll()
        self.model.select()
        self.setWidgets()
        # if self.titleTable == "Groups":
        #     self.setSpinBox()
        # elif self.titleTable == "Lesson":
        #     self.setSpinBox(1, 99999)  # добавляем spinbox
        #     self.setComboBox(3, self.DB.getTeacher())
        #
        # self.model.insertColumn(self.model.columnCount())  # для удаления
        # if self.titleTable == "Teacher" or self.titleTable == "Lesson":
        #     self.tableData.setColumnHidden(self.model.columnCount() - 2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
        # self.setBtnDel()
        self.tableData.scrollToBottom()   # пролистываем вниз
        self.clickBtnAdd = False

    def setBtnAdd(self):
        """добавляем кнопку добавления новой строки"""
        btnAdd = QtWidgets.QPushButton()
        self.layout.addWidget(btnAdd)
        btnAdd.clicked.connect(self.addRowTable)
        btnAdd.setStyleSheet("""background-color: rgb(255,255,255); text-align: center;""")
        btnAdd.setMinimumSize(30, 30)
        i = QIcon("add.png")
        btnAdd.setIcon(QtGui.QIcon(i))

    def delRowTable(self):
        """удаление строки из таблицы и бд при нажатии на кнопку"""
        btnDel = self.sender()
        row = self.tableData.indexAt(btnDel.pos()).row()
        column = self.DB.getTitleTable(self.titleTable, self.titlePKColumn)  # по названию возвращаем номер столбца
        dataId = self.model.index(row, column).data()
        self.DB.delRow(dataId, self.titleTable, self.titlePKColumn)   # из-за каскадного удаления
        self.model.submitAll()
        self.model.select()
        self.setWidgets()

    def setBtnDel(self):
        """установка кнопок удаления в таблицу"""
        row = self.model.rowCount()  # кол-во строк
        for y in range(row):
            btnDel = QPushButton()
            btnDel.setMinimumSize(30,30)
            btnDel.setMaximumSize(30, 30)   # x, y
            # btnDel.setStyleSheet("""text-align: center;""")
            i = QIcon("del.png")
            btnDel.setIcon(QtGui.QIcon(i))
            self.tableData.setIndexWidget(self.model.index(y, self.model.columnCount()-1), btnDel)
            btnDel.clicked.connect(lambda: self.delRowTable())

    def setSpinBox(self, column=1, max=5):
        @pyqtSlot()
        def setFromSpinBox(tableData):   # вызывается при установке значения из spinBox в БД
            self.model.submitAll()
            spinBox = self.sender()
            rowSpinBox = tableData.indexAt(spinBox.pos()).row()
            columnSpinBox = tableData.indexAt(spinBox.pos()).column()
            numForSet = spinBox.value() # вставляем число в бд
            record = self.model.record()
            for col in range(self.model.columnCount()-1):
                record.setValue(col, self.model.index(rowSpinBox, col).data())
                if col == columnSpinBox:
                    record.setValue(1, numForSet)
            self.model.updateRowInTable(rowSpinBox, record)

        for row in range(self.model.rowCount()):  # кол-во строк
            spinBox = QSpinBox()
            spinBox.setMaximum(max)
            spinBox.setMinimum(1)
            spinBox.setValue(self.model.index(row, column).data())   # вставляем в spinbox данные из ячейки
            self.tableData.setIndexWidget(self.model.index(row, column), spinBox)
            spinBox.editingFinished.connect(lambda: setFromSpinBox(self.tableData))

    # def setComboBox32(column, data):
    #     def setFromComboBox32(data, comboBox = None, rowComboBox = 123, columnComboBox=123):
    #         """при изменении значении в combobox вставляет это значение в БД"""
    #         self.changeTable()
    #         self.model.submitAll()
    #         record = self.model.record()
    #         if comboBox is None:
    #             comboBox = self.sender()
    #             # comboBox.setStyleSheet("""""")
    #             rowComboBox = self.tableData.indexAt(comboBox.pos()).row()
    #         # else:
    #         #     comboBox.setStyleSheet("""background-color:rgb(255,128,138);""")
    #         nowTeacher = comboBox.currentText()
    #
    #
    #         for textForSet in list(data.items()):     # ищем id учителя, чтобы вставить его в бд
    #             if nowTeacher in textForSet:
    #                 idNowTeacher = textForSet[0]
    #                 break
    #         print('ищем id в', list(data.items()))
    #         print('изменена в комбобоксе на', nowTeacher, idNowTeacher, 'позиция', comboBox, rowComboBox, columnComboBox)
    #
    #         for col in range(self.model.columnCount() - 1):
    #             record.setValue(col, self.model.index(rowComboBox, col).data())
    #             if col == columnComboBox:
    #                 record.setValue(col, idNowTeacher)
    #         # for i in range(self.model.columnCount()):
    #         #     print(record.value(i), end=' ')
    #         # self.model.submitAll()
    #         self.model.updateRowInTable(rowComboBox, record)
    #         self.model.submitAll()
    #
    #     dataForSet = list(data.values())
    #     print('вставляем в комбобокс', dataForSet)
    #     for row in range(self.model.rowCount()):
    #         comboBox = QComboBox()
    #         comboBox.addItems(dataForSet)
    #         self.tableData.setIndexWidget(self.model.index(row, column), comboBox)
    #         rowFalse = self.tableData.indexAt(comboBox.pos()).row()
    #         # print('строка', rowFalse, 'на самом деле -', row)
    #         print('позиция', comboBox, self.tableData.indexAt(comboBox.pos()).row(), self.tableData.indexAt(comboBox.pos()).column())
    #         idTeacher = self.model.index(row, column).data()     # берем текущее id учителя из таблицы
    #         if idTeacher != '':
    #             nowTeacher = data[idTeacher]        # по id находим имя учителя
    #             indTeacher = dataForSet.index(nowTeacher)
    #             comboBox.setCurrentIndex(indTeacher)       # вставляем индекс текущее имя в comboBox
    #             comboBox.currentIndexChanged.connect(lambda: setFromComboBox(data, columnComboBox=column))
    #         elif comboBox.currentText() != '':
    #             print('пусто')
    #             comboBox.currentIndexChanged.connect(lambda: setFromComboBox(data, columnComboBox=column))
    #             setFromComboBox(data, comboBox, self.tableData.indexAt(comboBox.pos()).row(), columnComboBox=column)

    def setFromComboBox(self):
        '''при изменении значении в combobox вставляем это значение в БД'''
        print('комбобокс изменен')
        comboBox = self.sender()
        # comboBox.setStyleSheet("""""")
        rowComboBox = self.tableData.indexAt(comboBox.pos()).row()
        columnComboBox = self.tableData.indexAt(comboBox.pos()).column()
        id = int(comboBox.currentText().split('|')[1])
        self.updateRow(rowComboBox, columnComboBox, id)

    def setComboBox(self, column, data):
        """
        вставка QCombobox в таблицу
        :param column: колонка куда вставляется QComboBox
        :param data: данные для вставки {id:data}
        """
        for row in range(self.model.rowCount()):
            comboBox = QComboBox()
            comboBox.addItems([v+' | '+str(k) for k, v in data.items()])
            nowId = self.model.index(row, column).data()  # берем из таблицы внешней ключ

            if nowId == '' and data:
                self.updateRow(row, column, int(comboBox.currentText().split('|')[1]))
                # comboBox.setStyleSheet("""background-color:rgb(255,128,138);""")
            elif nowId != '':
                comboBox.setCurrentText(data[nowId]+str(nowId))
            self.tableData.setIndexWidget(self.model.index(row, column), comboBox)
            comboBox.currentIndexChanged.connect(self.setFromComboBox)

            comboBox.setEditable(True)  # для поиска в comboBox
            comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
            # change completion mode of the default completer from InlineCompletion to PopupCompletion
            comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

    def updateRow(self, row, column, id):
        """
        обнавляем строку в таблице (при добавлении значения в бд из виджета)
        :param row:
        :param id:
        :return:
        """
        record = self.model.record()
        for col in range(self.model.columnCount() - 1):
            print(self.model.index(row, col).data())
            if col == column:
                record.setValue(col, id)
            else:
                record.setValue(col, self.model.index(row, col).data())
        self.model.updateRowInTable(row, record)

    def changeTable(self):
        """вызывается при изменении ячейки"""
        # print('ячейка изменена')
        # self.tableData.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        # self.tableData.horizontalHeader().setSectionResizeMode(0, 0)
        # self.tableData.horizontalHeader().setStretchLastSection(True)
        # self.tableData.resizeRowsToContents()
        # self.tableData.resizeColumnsToContents()
        # if not self.clickBtnAdd:    # я не знаю почему, но если вызывать submitAll при добавлении строки, то программа вылетает, но submitAll нужно вызывать, чтобы сразу же сохранить изменения в ячейки таблицы, а не после нажатия на enter
        #     self.model.submitAll()
        self.tableData.horizontalHeader().setStretchLastSection(True)
        self.tableData.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableData.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        pass

    def changeTab(self):
        """
        обновляется таблица для обновления данных в comboBox
        вызывается при переходе на вкладку 'Занятия'
        :return:
        """
        print('вкладка изменена на', self.tabWidget.currentIndex())

        # if self.titleTable == "Teacher" and self.ui.tabWidget.currentIndex() == 0:
        # elif self.titleTable == "Groups" and self.ui.tabWidget.currentIndex() == :
        if self.titleTable == "Lesson" and self.tabWidget.currentIndex() == 2:
            self.model.select()
            self.setWidgets()

    def setTableData(self):
        """установка данных в таблицу из БД """
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('Timetable.db')
        con.open()

        model = QSqlTableModel()
        model.setTable(self.titleTable)
        model.select()

        self.tableData.setModel(model)
        # self.tableData.verticalHeader().hide()   # спрятать цифры сбоку

        # self.setWidgets(self.model)
        # self.model.insertColumn(self.model.columnCount())    # для удаления
        # if self.titleTable == "Teacher" or self.titleTable == "Lesson":
        #     self.tableData.setColumnHidden(self.model.columnCount()-2, True)  # спрятать id (предпоследняя колонна) для Teacher or Lesson
        # # if self.titleTable == "Lesson":
        # #     self.model.insertColumn(self.model.columnCount()-1)    # для групп

        # for i, head in enumerate(self.headTable):
        #     self.model.setHeaderData(i, Qt.Horizontal, head)
        return model


def setStyle(ui):
    ui.setStyleSheet("""
    QPushButton { text-align: center;}
    QLabel {background-color: rgb(255,128,0);}
    """)

if __name__ == '__main__':
    import PyQt5_stylesheets

    app = QtWidgets.QApplication([])
    f = open('style_gray.qss')
    style = f.read()
    app.setStyleSheet(style)
    # app.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_gray"))
    f.close()

    win = MainWindow()
    sys.exit(app.exec_())

from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os

# subclass


# # the basic main()
# app = QtWidgets.QApplication(sys.argv)
# dialog = QtWidgets.QMainWindow()
# mainWidget = QtWidgets.QWidget()
# dialog.setCentralWidget(mainWidget)
# ComboBox = CheckableComboBox()
# for i in range(6):
#     ComboBox.addItem("Combobox Item " + str(i))
#
# dialog.show()
# sys.exit(app.exec_())

# if __name__ == "__main__":
#     qapp = QApplication(sys.argv)
#     window = MainWindow()
#
#     qapp.exec()

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
    #
    # def __init__(self):
    #     super().__init__()
    #     layout = Qt.QHBoxLayout(self)
    #     tab = QTableView()
    #     self.model = Qt.QStandardItemModel()
    #     self.modelsetRowCount(2)
    #     self.modelsetColumnCount(2)
    #     self.buttons = {}
    #     tab.setModel(model)
    #
    #     for y in range(2):
    #         btn = Qt.QPushButton("x")
    #         self.buttons[btn] = y
    #         btn.setObjectName(f'button{y}')
    #
    #         tab.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #         tab.setIndexWidget(self.modelindex(y, 0), QPushButton("button"))
    #
    #         # table.setCellWidget(y, 0, btn)
    #         btn.clicked.connect(lambda: self.out(tab))
    #
    #     layout.addWidget(tab)
    #     print(tab.indexAt(btn.pos()).row())
    #
    # def out(self, table):
    #     btn = self.sender()
    #     row = table.indexAt(btn.pos()).row()
    #     column = table.indexAt(btn.pos()).column()
    #     print(self.buttons[btn])

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
