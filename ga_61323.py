import sqlite3
import time
from copy import deepcopy

from deap import base, algorithms
from deap import creator
from deap import tools

import random
import matplotlib.pyplot as plt
import numpy as np

class Timer():
    def __init__(self):  # таймер
        self.st = time.time()

    def end(self):
        return float("%.2f" % (time.time() - self.st))

class DataBase():
    def __init__(self):
        self.con = sqlite3.connect('../../Downloads/Timetable.db')
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
          weekNumber INT,
          dayOfWeek INT,
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

        cur.execute("""CREATE TABLE IF NOT EXISTS TeacherAttendance
        (
          dayOfWeek INT,
          lessonNumber INT,
          teacherId INT,
          FOREIGN KEY (teacherId) REFERENCES Teacher(id) ON DELETE CASCADE ON UPDATE CASCADE
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

    def addTeacher(self, teacher):
        cur = self.con.cursor()
        cur.execute(f"""INSERT INTO Teacher VALUES (?,null)""", (teacher,))
        self.con.commit()

        cur.execute(f"""SELECT id FROM Teacher WHERE fullName = '{teacher}'""")
        for id in cur.fetchall():
            pass
        self.addTeacherTimeWork(id[0])
        cur.close()
        return id[0]

    def addLesson(self, teacher, hours, lesson):
        cur = self.con.cursor()
        cur.execute(f"""INSERT INTO Lesson VALUES (?,?,?,?,null)""", (lesson, hours, '', teacher))
        self.con.commit()

        cur.execute(f"""SELECT id FROM Lesson WHERE teacherId = '{teacher}'""")
        for id in cur.fetchall():
            pass
        cur.close()
        return id[0]

    def addGroup(self, group, courseNumber):
        cur = self.con.cursor()
        cur.execute(f"""INSERT INTO Groups VALUES (?,?)""", (group, courseNumber))
        self.con.commit()
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

    def getTitleGroup(self):
        cur = self.con.cursor()
        cur.execute("""SELECT title FROM Groups""")
        data = [d[0] for d in cur.fetchall()]
        cur.close()
        return data

    def delRow(self, id, titleTable, titlePKColumn):
        cur = self.con.cursor()
        cur.execute(f"""DELETE FROM {titleTable} WHERE {titlePKColumn} = '{id}'""")
        self.con.commit()
        cur.close()

    def addGroupLesson(self, id_lesson, title_group):
        cur = self.con.cursor()
        cur.execute(f"""INSERT INTO GroupLesson VALUES (?, ?)""", (id_lesson, title_group))
        self.con.commit()
        cur.close()

    def delGroupLesson(self, id_lesson, title_group):
        cur = self.con.cursor()
        cur.execute(f"""DELETE FROM GroupLesson WHERE lessonId = '{id_lesson}' AND groupTitle = '{title_group}'""")
        self.con.commit()
        cur.close()

    def getGroupLesson(self, idLesson):
        cur = self.con.cursor()
        cur.execute(f"""SELECT groupTitle FROM GroupLesson WHERE lessonId = '{idLesson}' """)
        data = [d[0] for d in cur.fetchall()]
        cur.close()
        return data

    def addTeacherTimeWork(self, id_teacher):
        cur = self.con.cursor()
        for day in range(6):
            for lesson in range(4):
                cur.execute(f"""INSERT INTO TeacherAttendance VALUES (?,?,?)""", (day, lesson, id_teacher))
        self.con.commit()
        cur.close()

    def getTeacherTimeWork(self, id_teacher):
        cur = self.con.cursor()
        timeWork = [[False, False, False, False] for _ in range(6)]
        cur.execute(f"""SELECT dayOfWeek, lessonNumber FROM TeacherAttendance WHERE teacherId = {id_teacher}""")
        for day, lesson in cur.fetchall():
            timeWork[day][lesson] = True
        return timeWork

    def add_work_day(self, day, les, id):
        """удаление и добавление рабочего дня для учителя"""
        cur = self.con.cursor()
        cur.execute("""INSERT INTO TeacherAttendance VALUES (?,?,?)""", (day, les, id))
        self.con.commit()
        cur.close()

    def get_teachers_for_group_in_day(self):
        """для генерации расписания {day:{numLesson:{group:[teachers]}}}"""
        cur = self.con.cursor()
        cur.execute("""SELECT DISTINCT TeacherAttendance.dayOfWeek, TeacherAttendance.lessonNumber, GroupLesson.groupTitle, TeacherAttendance.teacherId
                        FROM GroupLesson, Lesson, TeacherAttendance WHERE TeacherAttendance.teacherId = Lesson.teacherId and GroupLesson.lessonId = Lesson.id""")
        data = {}
        for day, numLesson, group, teacher in cur.fetchall():
            if day not in data.keys():
                data[day] = {}
            if numLesson not in data[day].keys():
                data[day][numLesson] = {}
            if group not in data[day][numLesson].keys():
                data[day][numLesson][group] = []
            data[day][numLesson][group].append(teacher)
        return data

    def get_group_teacher_lesson(self):
        """{group:teacher:[[lessonID, quantityLessonForTwoWeek], ...]}"""
        cur = self.con.cursor()
        cur.execute("""SELECT DISTINCT GroupLesson.groupTitle, Lesson.teacherId, GroupLesson.lessonId, Lesson.hour FROM GroupLesson, Lesson WHERE GroupLesson.lessonId = Lesson.id""")
        query = cur.fetchall()
        data = {}
        group_hours = self.get_hours_group()
        for group, teacher, lesson, hour in query:
            if group not in data.keys():
                data[group] = {}
                group_hours[group] //= 36   # получаем кол-во учебных недель
            if teacher not in data[group].keys():
                data[group][teacher] = []
            data[group][teacher].append([lesson, hour//group_hours[group]])
        return data, group_hours

    def get_hours_group(self):
        """общее кол-во часов для группы за семестр"""
        cur = self.con.cursor()
        cur.execute("""SELECT GroupLesson.groupTitle, SUM(Lesson.hour) FROM GroupLesson, Lesson WHERE Lesson.id = GroupLesson.lessonId GROUP BY GroupLesson.groupTitle""")
        group_hours = {}
        for group, hours in cur.fetchall():
            group_hours[group] = hours
        cur.close()
        return group_hours

    def getAllTeacherTimeWork(self):
        """получение всех возможных дней работы учителей"""
        cur = self.con.cursor()
        cur.execute("""SELECT id FROM Teacher""")
        teacherID_TimeWork = {}
        for id in cur.fetchall():
            id = id[0]
            teacherID_TimeWork[id] = [self.getTeacherTimeWork(id), self.getTeacherTimeWork(id)]

        cur.close()
        return teacherID_TimeWork

    def get_group_lesson(self):
        cur = self.con.cursor()
        cur.execute(
            """SELECT Lesson.hour, lessonId, groupTitle FROM GroupLesson, Lesson WHERE GroupLesson.lessonId = Lesson.id ORDER BY groupTitle""")
        number_free_lessons = 12
        group_lesson = []
        group_hours = self.get_hours_group()
        # print(group_hours)
        index_lesson = []
        index_group = []
        group_before = None
        for hour, lesson, group in cur.fetchall():
            if group_before != group:
                group_before = group
                i = 0 + number_free_lessons
                group_lesson.append([i for i in range(number_free_lessons)])
                index_group.append(group)
                index_lesson.append([None] * number_free_lessons)
            group_lesson[-1] += [i for i in range(i, i + hour // (group_hours[group] // 36))]
            i += hour // (group_hours[group] // 36)
            index_lesson[-1] += [lesson] * (hour // (group_hours[group] // 36))

            # print([lesson]*(hour//(group_hours[group]//36)))
            # print(lesson, hour//(group_hours[group]//36), hour, group, group_hours[group])
        return group_lesson, index_lesson, index_group

    def get_lessonID_teacherID(self):
        cur = self.con.cursor()
        cur.execute("""SELECT id, teacherId FROM Lesson""")
        lessonID_teacherID = {}
        for lessonID, teacherID in cur.fetchall():
            lessonID_teacherID[lessonID] = teacherID
        cur.close()
        return lessonID_teacherID

    def insert_time_table(self, timeTable):
        cur = self.con.cursor()
        cur.execute("""DELETE FROM GroupTimetable""")
        # weekNumber dayOfWeek lessonNumber lessonId
        for group_lesson in timeTable:
            for week in range(2):
                for day in range(6):
                    for num_lesson in range(4):
                        num = week*6*4 + day*4 + num_lesson
                        lesson = group_lesson[num]
                        if lesson != None:
                            cur.execute("""INSERT INTO GroupTimetable VALUES (?,?,?,?)""", (week, day, num_lesson, lesson))
        cur.close()
        self.con.commit()


class GeneticGenerationTimeTable():
    def __init__(self):
        """запросы к бд + 1 поколение"""
        self.DB = DataBase()
        self.group_lesson, self.index_lesson, self.index_group = self.DB.get_group_lesson()  # id_lesson - по индексу обращаемся к уроку
        self.teacherID_TimeWork = self.DB.getAllTeacherTimeWork()  # {teacherID:[{day:{numLesson:True|False}}, day:{numLesson:True|False}}]} - 2 недели
        # self.group_lesson = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
        # self.index_lesson = [[None, 1, 3], [None, 2, 4]]
        # self.teacherID_TimeWork = {1: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 2: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]]}
        # self.lesson_teacherID = {1: 1, 2: 1, 3: 1, 4: 1}


        # более полные данные
        # self.group_lesson = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 5, 6, 7, 7, 8, 8, 8, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 9, 10, 10, 10, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 5, 6, 7, 7, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 6, 6, 6, 7, 7, 8, 8, 8, 9, 9, 10, 11, 11, 11, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 10, 11, 11, 11, 12, 13, 13, 13, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 9, 10, 10, 10, 11, 12, 12, 12, 12, 12, 12, 13, 13, 14, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 7, 8, 9, 9, 10, 10, 10, 11, 11, 11, 11, 11, 11, 12, 12, 13, 14, 14, 14, 14, 14, 15, 16, 16], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 9, 9, 10, 10, 10, 11, 11, 11, 11, 11, 11, 12, 12, 12, 13, 13, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 9, 9, 10, 10, 10, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14]]
        # self.index_lesson = [None, 7, 8, 9, 24, 38, 52, 53, 67, 81, 91, 92, 112, 115, 124, None, 22, 29, 34, 44, 45, 72, 77, 86, 98, 99, 100, 110, 113, 117, None, 4, 5, 6, 31, 36, 48, 49, 74, 79, 88, 111, 114, 119, 121, None, 11, 30, 35, 46, 47, 62, 73, 78, 87, 101, 102, 103, 118, 120, None, 16, 26, 40, 56, 57, 69, 83, 94, 95, 107, 108, 109, 116, 126, None, 23, 37, 50, 51, 63, 80, 89, 90, 104, 105, 106, 122, 123, 127, None, 17, 18, 19, 20, 27, 41, 58, 59, 60, 65, 70, 75, 84, 96, 97, 128, None, 12, 13, 14, 15, 25, 32, 39, 54, 55, 64, 68, 82, 93, 125, None, 1, 2, 3, 10, 21, 28, 33, 42, 43, 61, 66, 71, 76, 85]
        # self.teacherID_TimeWork = {1: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 2: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 3: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 4: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 5: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 6: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 7: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 8: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 9: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 10: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 11: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 12: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 13: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 14: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 15: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 16: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 17: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 18: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]], 19: [[[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]], [[True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True], [True, True, True, True]]]}
        # self.lesson_teacherID = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2, 19: 2, 20: 2, 21: 3, 22: 3, 23: 3, 24: 3, 25: 3, 26: 3, 27: 3, 28: 4, 29: 4, 30: 4, 31: 4, 32: 4, 33: 5, 34: 5, 35: 5, 36: 5, 37: 5, 38: 5, 39: 5, 40: 5, 41: 5, 42: 6, 43: 6, 44: 6, 45: 6, 46: 6, 47: 6, 48: 6, 49: 6, 50: 6, 51: 6, 52: 6, 53: 6, 54: 6, 55: 6, 56: 6, 57: 6, 58: 6, 59: 6, 60: 6, 61: 7, 62: 7, 63: 7, 64: 7, 65: 7, 66: 8, 67: 8, 68: 8, 69: 8, 70: 8, 71: 9, 72: 9, 73: 9, 74: 9, 75: 9, 76: 10, 77: 10, 78: 10, 79: 10, 80: 10, 81: 10, 82: 10, 83: 10, 84: 10, 85: 11, 86: 11, 87: 11, 88: 11, 89: 11, 90: 11, 91: 11, 92: 11, 93: 11, 94: 11, 95: 11, 96: 11, 97: 11, 98: 12, 99: 12, 100: 12, 101: 12, 102: 12, 103: 12, 104: 12, 105: 12, 106: 12, 107: 12, 108: 12, 109: 12, 110: 13, 111: 13, 112: 13, 113: 14, 114: 14, 115: 14, 116: 14, 117: 15, 118: 16, 119: 16, 120: 17, 121: 17, 122: 17, 123: 17, 124: 17, 125: 17, 126: 17, 127: 18, 128: 19}
        # self.index_group = None # пока не надо

        self.lesson_teacherID = self.DB.get_lessonID_teacherID()
        print(self.group_lesson, self.index_lesson, self.teacherID_TimeWork, self.lesson_teacherID, sep='\n')

    def random_timeTable(self):
        """первое поколение"""
        TimeTable = deepcopy(self.group_lesson)
        for num_group in range(len(TimeTable)):
            random.shuffle(TimeTable[num_group])
        return creator.Individual(TimeTable)

    def TimeTable_Fitness(self, individual):
        fitness = 0
        teacherID_TimeWork = deepcopy(self.teacherID_TimeWork)
        for num_group in range(len(individual)):
            for week in range(0, 2):
                count_lesson_week = 0
                for day in range(0, 6):
                    windowsGroup = False
                    count_lesson_day = 0
                    for numLesson in range(week*6*4 + day*4, week*6*4 + day*4 + 4):
                        lesson = self.index_lesson[num_group][individual[num_group][numLesson]]
                        if lesson != None:    # кол-во пар в день
                            if windowsGroup:    # после (окна свободное время) значит это окно
                                windowsGroup = 2
                            count_lesson_day += 1
                            if not teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][numLesson%4]:    # если у учителя нет этой пары (методичсеский дни)
                                fitness += 5
                            elif teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][numLesson%4] == True:  # отмеаем, что пара
                                teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][numLesson%4] = -1
                            else:   # уже есть пара
                                fitness += 50
                        elif count_lesson_day >= 1:     # нет пары (окно)
                            windowsGroup = True

                    if windowsGroup == 2:
                        fitness += 20
                    if count_lesson_day <= 1:
                        fitness += 50 * (count_lesson_day+1)
                    count_lesson_week += count_lesson_day

                fitness += 5 * abs(18-count_lesson_week) # должно быть 18 пар в неделю
        # self.all_fitness.append(fitness)
        # print(sum(self.all_fitness)//len(self.all_fitness))
        return fitness,

    def cxOrder(self, ind1, ind2):
        # for num_group in range(0, len(ind1), 2):
        #     ind1[num_group], ind2[num_group] = ind2[num_group], ind1[num_group]
        size = min(len(ind1[0]), len(ind2[0]))
        a, b = random.sample(range(size), 2)
        for group1, group2 in zip(ind1, ind2):
            tools.cxOrdered(group1, group2,a,b,size)
        return ind1, ind2

    def mutationTimeTable(self, individual, indpb):
        for numGroup in range(len(individual)):
            for i in range(len(individual[numGroup])):
                # tools.mutShuffleIndexes(individual, indpb)
                if random.random() < 0.1:
                    random_gen = random.randint(0, len(individual[numGroup])-1)
                    individual[numGroup][i], individual[numGroup][random_gen] = individual[numGroup][random_gen], individual[numGroup][i]
        return individual,

    def save_TimeTable_in_DB(self, TimeTable):
        # self.DB.insert_time_table
        TimeTable_for_save = []
        for num_group, group in enumerate(TimeTable):
            TimeTable_for_save.append([])
            for ind_lesson in group:
                TimeTable_for_save[-1].append(self.index_lesson[num_group][ind_lesson])
        # print(TimeTable_for_save)
        self.DB.insert_time_table(TimeTable_for_save)



generation = GeneticGenerationTimeTable()
less_none = 0
less_1 = 12
less_2 = 30
timeTable = [[],[]]
for num_day in range(6):
    timeTable[0]+=[less_1, less_1+1, less_1+2, less_none]
    less_1 += 3
    less_none += 1
for num_day in range(6):
    timeTable[0]+=[less_2, less_2+1, less_2+2, less_none]
    less_2 += 3
    less_none += 1
timeTable[1] = deepcopy(timeTable[0][::-1])
print(timeTable)
# print(generation.TimeTable_Fitness(timeTable))
generation.save_TimeTable_in_DB(timeTable)

# константы генетического алгоритма
POPULATION_SIZE = 1000               # количество индивидуумов в популяции
P_CROSSOVER = 0.9                   # вероятность скрещивания
P_MUTATION= 0        # вероятность мутации индивидуума
MAX_GENERATIONS = 50    # максимальное количество поколений
HALL_OF_FAME_SIZE = 1

hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox = base.Toolbox()
toolbox.register('random_timeTable', generation.random_timeTable)
toolbox.register('populationCreator', tools.initRepeat, list, toolbox.random_timeTable)

population = toolbox.populationCreator(n=POPULATION_SIZE)

toolbox.register("evaluate", generation.TimeTable_Fitness)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", generation.cxOrder)
toolbox.register("mutate", generation.mutationTimeTable, indpb=P_MUTATION)

stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("min", np.min)
stats.register("avg", np.mean)
while 1:
    # MAX_GENERATIONS = int(input())
    t = Timer()
    population, logbook = algorithms.eaSimple(population, toolbox,
                                            cxpb=P_CROSSOVER,
                                            mutpb=P_MUTATION,
                                            ngen=MAX_GENERATIONS,
                                            halloffame=hof,
                                            stats=stats,
                                            verbose=True)

    # best = hof.items[0]
    # print(best)

    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")
    # print(minFitnessValues, meanFitnessValues)
    plt.plot(minFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Поколение')
    plt.ylabel('Мин/средняя приспособленность')
    plt.title('Зависимость минимальной и средней приспособленности от поколения')
    min_fitness = 100000
    ind_min_fitness = 0
    for i in range(len(population)):
        fitness = generation.TimeTable_Fitness(population[i])[0]
        if fitness < min_fitness:
            min_fitness = fitness
            ind_min_fitness = i
    print(population[ind_min_fitness])
    print(min_fitness)
    print(t.end(),' секунд\n', (meanFitnessValues[0]-meanFitnessValues[-1])//t.end(), '- приспособленность в секунду')
    print(meanFitnessValues[0],meanFitnessValues[-1])
    print(meanFitnessValues[0]-meanFitnessValues[-1])
    plt.show()

# 30000, 0.15
# [[2, 0, 5, 0, 8, 5, 13, 13, 0, 7, 9, 8, 7, 5, 2, 9, 0, 0, 12, 9, 0, 8, 8, 2, 9, 5, 0, 0, 0, 2, 5, 8, 0, 0, 4, 8, 0, 8, 12, 7, 0, 6, 8, 4, 0, 0, 12, 5], [0, 0, 3, 14, 0, 10, 1, 1, 14, 13, 1, 14, 0, 0, 7, 10, 0, 9, 10, 1, 7, 1, 14, 12, 14, 12, 0, 0, 0, 0, 0, 0, 3, 14, 0, 0, 0, 6, 14, 2, 5, 14, 5, 12, 12, 14, 3, 10], [6, 3, 0, 0, 0, 10, 14, 9, 0, 14, 0, 9, 10, 8, 8, 2, 14, 13, 4, 8, 11, 13, 5, 5, 0, 0, 14, 5, 14, 9, 7, 12, 0, 0, 11, 14, 0, 0, 7, 4, 14, 8, 12, 14, 7, 12, 5, 9], [8, 8, 8, 3, 11, 0, 0, 7, 0, 8, 14, 14, 0, 0, 14, 6, 3, 14, 8, 14, 14, 14, 0, 0, 0, 6, 3, 3, 0, 11, 8, 7, 14, 0, 14, 0, 0, 0, 8, 14, 3, 3, 14, 8, 8, 0, 0, 14], [0, 0, 6, 13, 6, 2, 0, 0, 0, 3, 6, 6, 1, 2, 11, 8, 0, 0, 2, 6, 8, 6, 2, 8, 0, 0, 0, 0, 6, 13, 3, 1, 6, 13, 3, 11, 0, 13, 3, 13, 0, 11, 3, 1, 3, 8, 8, 0], [5, 5, 0, 6, 0, 12, 6, 5, 0, 0, 0, 0, 13, 12, 0, 0, 0, 6, 6, 12, 0, 0, 0, 0, 0, 0, 12, 6, 12, 5, 0, 0, 11, 6, 13, 12, 5, 12, 9, 12, 0, 0, 4, 10, 10, 0, 0, 6], [14, 14, 14, 11, 14, 14, 5, 14, 11, 5, 14, 11, 14, 14, 5, 14, 11, 5, 14, 11, 0, 5, 11, 14, 11, 14, 5, 14, 0, 14, 14, 14, 0, 0, 5, 6, 14, 5, 5, 5, 0, 5, 10, 5, 14, 11, 14, 13], [10, 10, 11, 9, 3, 0, 11, 0, 0, 0, 10, 1, 0, 0, 11, 5, 6, 11, 0, 5, 0, 0, 6, 6, 3, 13, 11, 10, 11, 6, 0, 0, 0, 2, 7, 5, 0, 14, 13, 11, 0, 0, 14, 7, 4, 7, 11, 2], [0, 6, 13, 5, 4, 0, 0, 10, 0, 10, 5, 12, 0, 11, 4, 13, 5, 2, 0, 0, 0, 11, 4, 11, 0, 11, 7, 0, 0, 0, 11, 5, 0, 11, 0, 2, 11, 11, 10, 0, 11, 0, 6, 0, 0, 9, 6, 0]]
# 1160
# 4526.48
#  1.0 - приспособленность в секунду
# 6351.94 1324.58
# 5027.36

# 2000, 0.5
# [[12, 12, 7, 13, 0, 2, 12, 8, 8, 0, 0, 2, 0, 8, 8, 12, 2, 0, 13, 0, 13, 0, 7, 0, 14, 8, 8, 8, 0, 8, 8, 8, 0, 0, 8, 9, 0, 8, 8, 8, 1, 9, 0, 0, 0, 8, 14, 12], [2, 8, 0, 0, 14, 14, 14, 5, 7, 12, 3, 7, 2, 0, 0, 8, 0, 0, 14, 14, 0, 12, 1, 2, 0, 14, 14, 12, 0, 14, 7, 0, 0, 3, 3, 4, 7, 0, 0, 3, 0, 12, 5, 2, 0, 1, 1, 13], [11, 14, 5, 14, 4, 4, 4, 14, 14, 5, 5, 4, 10, 5, 14, 14, 14, 11, 0, 0, 0, 0, 0, 0, 0, 0, 13, 5, 14, 13, 14, 10, 0, 14, 4, 14, 0, 0, 13, 4, 14, 14, 0, 0, 10, 12, 13, 5], [0, 5, 13, 8, 13, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 11, 0, 0, 0, 0, 0, 0, 11, 13, 13, 5, 0, 0, 0, 0, 0, 0, 11, 0, 11, 0, 13, 5, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 3, 0, 6, 0, 0, 7, 7, 0, 0, 7, 5, 0, 7, 9, 5, 14, 0, 0, 6], [0, 0, 10, 7, 3, 0, 0, 12, 0, 0, 12, 14, 0, 10, 7, 0, 0, 12, 12, 12, 14, 7, 0, 0, 2, 2, 10, 10, 2, 0, 12, 0, 2, 0, 0, 8, 2, 7, 14, 7, 0, 13, 13, 14, 12, 0, 12, 0], [0, 0, 8, 5, 5, 5, 3, 11, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 3, 3, 11, 3, 0, 0, 0, 11, 3, 0, 0, 0, 3, 3, 0, 0, 9, 3, 10, 2, 11, 12, 0, 3, 0, 7, 3, 14, 0, 0], [13, 3, 3, 2, 0, 0, 11, 2, 0, 11, 0, 11, 0, 2, 11, 5, 6, 3, 6, 11, 2, 5, 0, 0, 0, 0, 7, 2, 0, 0, 3, 5, 6, 11, 5, 10, 0, 0, 3, 11, 6, 11, 3, 4, 0, 0, 6, 11], [0, 11, 12, 4, 10, 7, 5, 6, 11, 0, 7, 0, 0, 4, 5, 11, 10, 6, 10, 7, 0, 10, 13, 13, 13, 7, 0, 0, 11, 4, 0, 0, 0, 0, 10, 12, 5, 0, 4, 0, 12, 5, 6, 11, 0, 0, 11, 4]]
# 1705
# 156.16???  секунд
#  2.0??? - приспособленность в секунду
# 2170.64 1790.62
# 380.02

# 2000 0.8
# [[11, 12, 11, 11, 0, 12, 12, 9, 12, 9, 11, 11, 9, 0, 9, 0, 0, 0, 8, 12, 0, 9, 12, 8, 0, 12, 0, 12, 0, 0, 8, 8, 8, 12, 8, 0, 1, 9, 0, 0, 0, 0, 9, 14, 0, 8, 12, 12], [14, 13, 0, 0, 1, 0, 0, 2, 0, 0, 3, 8, 14, 10, 10, 14, 0, 13, 3, 10, 0, 13, 1, 6, 14, 3, 1, 5, 14, 4, 0, 0, 2, 2, 6, 0, 0, 3, 5, 13, 13, 14, 14, 8, 1, 0, 0, 14], [5, 14, 13, 4, 14, 4, 0, 0, 0, 8, 7, 14, 0, 2, 14, 4, 4, 9, 14, 9, 0, 0, 13, 10, 0, 0, 9, 9, 0, 13, 2, 14, 0, 0, 5, 7, 0, 0, 9, 5, 9, 9, 5, 13, 0, 5, 2, 10], [0, 3, 14, 6, 6, 11, 1, 0, 5, 14, 14, 9, 3, 0, 1, 0, 8, 8, 13, 14, 0, 8, 14, 2, 11, 0, 0, 3, 0, 11, 9, 13, 0, 8, 13, 2, 0, 0, 1, 2, 0, 0, 11, 5, 0, 11, 11, 0], [6, 9, 9, 5, 0, 6, 6, 5, 6, 6, 9, 6, 13, 6, 13, 6, 0, 5, 6, 6, 0, 0, 0, 0, 0, 9, 6, 13, 11, 6, 6, 7, 0, 14, 3, 13, 0, 0, 0, 0, 1, 3, 2, 9, 0, 0, 13, 2], [2, 5, 12, 13, 0, 0, 8, 14, 14, 13, 5, 5, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 8, 14, 7, 2, 0, 0, 0, 6, 12, 0, 14, 6, 14, 7, 7, 7, 2, 6, 12, 0, 0, 6], [0, 0, 2, 9, 0, 0, 14, 10, 11, 2, 16, 0, 0, 0, 0, 0, 2, 14, 0, 0, 14, 14, 0, 0, 0, 0, 11, 11, 5, 5, 5, 11, 11, 5, 14, 14, 0, 0, 11, 4, 0, 5, 13, 16, 10, 9, 14, 0], [0, 0, 2, 1, 0, 3, 11, 13, 2, 11, 0, 2, 11, 0, 0, 11, 0, 2, 11, 2, 11, 2, 11, 0, 12, 0, 12, 0, 0, 0, 0, 0, 0, 11, 11, 12, 11, 11, 12, 11, 0, 11, 12, 11, 7, 7, 0, 0], [0, 6, 7, 14, 11, 5, 5, 6, 0, 0, 13, 4, 7, 13, 0, 0, 0, 11, 0, 5, 2, 12, 5, 5, 2, 7, 14, 7, 2, 12, 11, 2, 14, 4, 4, 11, 13, 0, 13, 0, 11, 4, 0, 2, 0, 0, 0, 0]]
# 1235
# 319.59  секунд
#  15.0 - приспособленность в секунду
# 6363.46 1351.14
# 5012.32

# 2000 1.5
# [[0, 4, 5, 11, 12, 8, 0, 0, 0, 12, 14, 8, 2, 13, 12, 4, 0, 12, 9, 5, 0, 0, 0, 0, 0, 2, 4, 12, 0, 0, 3, 13, 0, 8, 13, 5, 0, 14, 8, 8, 9, 4, 2, 8, 0, 0, 11, 8], [0, 12, 10, 14, 14, 3, 0, 0, 2, 0, 0, 10, 0, 0, 14, 12, 10, 14, 12, 0, 2, 3, 8, 3, 0, 14, 13, 10, 14, 0, 0, 14, 2, 10, 14, 0, 0, 0, 13, 10, 14, 8, 8, 14, 0, 8, 13, 12], [11, 14, 0, 0, 0, 12, 9, 14, 0, 0, 8, 9, 0, 12, 4, 14, 5, 5, 14, 14, 14, 12, 14, 4, 0, 0, 5, 5, 5, 5, 0, 0, 8, 9, 4, 14, 0, 11, 5, 9, 12, 5, 5, 11, 0, 14, 4, 3], [14, 8, 13, 2, 2, 4, 0, 0, 14, 8, 11, 3, 8, 1, 0, 0, 0, 0, 11, 13, 0, 5, 3, 8, 0, 0, 1, 14, 1, 0, 14, 0, 14, 5, 2, 13, 14, 0, 2, 0, 11, 6, 0, 0, 14, 11, 3, 14], [6, 5, 6, 7, 7, 0, 1, 0, 0, 3, 0, 7, 7, 5, 0, 0, 0, 1, 6, 8, 0, 0, 6, 6, 8, 0, 0, 6, 6, 6, 6, 6, 0, 3, 6, 8, 3, 1, 11, 4, 0, 3, 6, 0, 8, 1, 0, 0], [12, 13, 0, 0, 0, 14, 14, 12, 0, 0, 2, 5, 0, 0, 2, 5, 0, 10, 2, 12, 0, 0, 12, 10, 2, 12, 0, 0, 0, 0, 12, 5, 12, 12, 12, 12, 0, 0, 12, 14, 0, 10, 12, 13, 2, 12, 0, 5], [3, 1, 0, 0, 9, 0, 0, 2, 0, 11, 5, 14, 11, 9, 5, 2, 14, 0, 0, 3, 11, 14, 5, 14, 0, 10, 14, 3, 11, 2, 10, 10, 0, 0, 11, 11, 0, 5, 14, 0, 0, 14, 14, 12, 0, 0, 6, 10], [0, 11, 2, 12, 0, 11, 4, 11, 6, 0, 12, 0, 5, 14, 11, 3, 2, 0, 0, 7, 12, 11, 0, 0, 0, 5, 12, 0, 0, 14, 5, 2, 0, 0, 5, 3, 11, 0, 6, 5, 1, 3, 11, 3, 0, 0, 14, 6], [0, 0, 0, 0, 11, 7, 11, 7, 5, 13, 6, 4, 0, 10, 9, 10, 6, 0, 0, 11, 7, 4, 11, 5, 10, 13, 11, 4, 0, 0, 0, 0, 11, 13, 0, 0, 0, 4, 9, 3, 0, 0, 4, 6, 10, 5, 0, 0]]
# 1095
# 412.86  секунд
#  12.0 - приспособленность в секунду
# 6344.82 1210.22
# 5134.599999999999

# 2000 1.5
# [[0, 10, 4, 10, 0, 0, 8, 12, 10, 0, 8, 0, 8, 8, 0, 0, 0, 0, 8, 8, 0, 8, 0, 8, 0, 0, 12, 8, 0, 0, 8, 8, 0, 13, 10, 0, 0, 0, 13, 11, 11, 12, 11, 8, 0, 0, 14, 9], [0, 1, 12, 3, 0, 12, 14, 8, 0, 0, 14, 14, 0, 10, 11, 10, 0, 13, 13, 2, 8, 10, 0, 13, 13, 10, 0, 0, 0, 14, 10, 0, 0, 0, 14, 2, 6, 7, 1, 0, 0, 13, 14, 0, 0, 0, 12, 12], [0, 0, 9, 13, 14, 4, 0, 0, 14, 6, 13, 4, 12, 14, 14, 4, 14, 0, 14, 0, 0, 13, 13, 14, 8, 0, 14, 0, 0, 0, 9, 2, 0, 10, 2, 8, 0, 13, 12, 8, 13, 0, 13, 0, 14, 14, 13, 4], [0, 14, 1, 14, 7, 0, 0, 14, 6, 11, 0, 5, 6, 0, 0, 1, 7, 14, 6, 7, 11, 14, 6, 0, 6, 0, 11, 0, 6, 0, 7, 0, 1, 0, 6, 0, 0, 12, 14, 4, 14, 1, 0, 0, 7, 6, 11, 11], [0, 0, 6, 8, 0, 6, 5, 13, 2, 0, 2, 0, 2, 6, 13, 8, 0, 0, 1, 6, 0, 2, 5, 6, 0, 8, 7, 2, 0, 9, 7, 6, 7, 6, 9, 7, 0, 0, 9, 7, 6, 7, 3, 6, 3, 0, 6, 0], [13, 6, 14, 7, 0, 0, 13, 1, 0, 0, 7, 1, 0, 12, 12, 12, 12, 0, 0, 12, 14, 7, 0, 0, 0, 14, 1, 7, 0, 7, 12, 14, 0, 1, 12, 12, 0, 0, 7, 13, 0, 14, 0, 13, 0, 13, 4, 14], [10, 12, 10, 5, 0, 0, 6, 10, 0, 0, 6, 10, 11, 0, 0, 5, 3, 11, 10, 5, 5, 0, 0, 10, 10, 0, 0, 11, 0, 0, 14, 13, 0, 8, 13, 0, 8, 14, 11, 14, 15, 11, 16, 3, 12, 3, 3, 1], [0, 0, 11, 11, 0, 11, 3, 10, 12, 14, 0, 0, 0, 1, 6, 6, 10, 9, 6, 14, 6, 9, 11, 12, 14, 0, 9, 0, 14, 10, 3, 5, 10, 5, 0, 0, 10, 5, 0, 0, 0, 0, 5, 11, 5, 0, 0, 6], [6, 9, 0, 0, 10, 14, 11, 7, 0, 2, 11, 7, 0, 4, 2, 0, 0, 6, 12, 11, 2, 5, 12, 5, 4, 6, 7, 4, 11, 2, 7, 10, 14, 0, 0, 11, 0, 11, 0, 2, 2, 5, 7, 14, 11, 11, 0, 0]]
# 1430
# 390.16  секунд
#  12.0 - приспособленность в секунду
# 6343.48 1610.13
# 4733.349999999999

# 2000 1.5 1.8
# [[10, 8, 8, 4, 2, 8, 8, 5, 0, 10, 8, 10, 0, 0, 5, 11, 0, 0, 2, 4, 0, 0, 4, 8, 0, 5, 5, 0, 11, 12, 0, 0, 0, 0, 8, 8, 0, 10, 8, 12, 10, 2, 8, 10, 0, 0, 7, 13], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 0, 3, 0, 0, 0, 13, 3, 5, 5, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 3, 9, 3, 0, 0], [0, 5, 14, 0, 13, 14, 12, 13, 0, 5, 9, 12, 7, 9, 4, 5, 0, 5, 9, 13, 0, 0, 7, 9, 13, 12, 0, 7, 14, 0, 9, 0, 0, 0, 9, 12, 12, 0, 12, 0, 0, 0, 12, 4, 13, 14, 13, 14], [2, 13, 13, 13, 0, 7, 13, 1, 1, 8, 2, 8, 0, 14, 0, 8, 8, 2, 0, 0, 0, 0, 14, 2, 0, 0, 7, 8, 0, 0, 8, 14, 0, 1, 1, 1, 0, 0, 14, 2, 8, 0, 0, 14, 2, 13, 0, 0], [6, 3, 3, 5, 11, 3, 5, 14, 0, 0, 14, 14, 0, 0, 11, 6, 0, 7, 6, 6, 0, 6, 5, 6, 0, 6, 14, 11, 0, 0, 0, 0, 0, 7, 5, 6, 0, 5, 5, 6, 6, 14, 6, 5, 7, 6, 14, 12], [14, 10, 12, 12, 0, 0, 4, 12, 4, 4, 12, 4, 0, 0, 0, 0, 12, 12, 13, 12, 0, 0, 12, 12, 12, 14, 0, 0, 0, 0, 7, 13, 14, 13, 4, 0, 0, 13, 7, 13, 0, 0, 4, 13, 10, 0, 12, 0], [0, 0, 10, 2, 12, 0, 14, 0, 12, 14, 5, 3, 0, 15, 14, 12, 2, 0, 0, 14, 11, 16, 0, 0, 11, 2, 0, 0, 0, 2, 16, 12, 0, 12, 12, 14, 10, 3, 10, 10, 2, 0, 11, 0, 14, 11, 3, 3], [0, 6, 5, 6, 0, 11, 3, 11, 11, 3, 0, 0, 11, 0, 3, 0, 5, 11, 11, 11, 0, 12, 11, 11, 0, 11, 11, 5, 12, 11, 11, 11, 11, 0, 0, 9, 0, 8, 2, 4, 0, 5, 3, 12, 0, 0, 11, 11], [0, 9, 6, 14, 7, 4, 6, 7, 9, 13, 13, 13, 9, 13, 0, 0, 11, 14, 4, 2, 0, 0, 13, 5, 0, 13, 2, 12, 0, 6, 5, 2, 0, 0, 11, 11, 7, 0, 0, 9, 4, 7, 14, 6, 4, 4, 9, 9]]
# 1230
# 457.17  секунд
#  10.0 - приспособленность в секунду
# 6347.26 1453.41
# 4893.85

# 2000 1.5 5
# [[5, 5, 5, 8, 0, 8, 8, 5, 0, 5, 5, 8, 0, 0, 0, 0, 8, 5, 8, 8, 8, 5, 5, 5, 0, 0, 8, 8, 8, 5, 8, 8, 8, 8, 5, 5, 0, 0, 8, 8, 0, 8, 8, 8, 0, 0, 8, 5], [13, 13, 8, 14, 14, 0, 0, 13, 0, 13, 8, 13, 14, 14, 1, 8, 0, 1, 14, 1, 0, 14, 13, 13, 1, 8, 14, 13, 0, 0, 0, 0, 14, 14, 8, 13, 8, 8, 14, 13, 0, 14, 14, 14, 0, 1, 13, 8], [11, 11, 14, 4, 12, 14, 9, 9, 0, 4, 14, 9, 4, 12, 12, 9, 0, 0, 4, 4, 11, 12, 0, 0, 9, 12, 9, 0, 0, 0, 12, 12, 0, 4, 12, 4, 0, 0, 9, 12, 9, 9, 4, 4, 4, 4, 14, 11], [0, 0, 0, 0, 0, 0, 14, 8, 14, 8, 0, 14, 8, 0, 8, 0, 14, 0, 0, 14, 0, 0, 14, 9, 0, 0, 0, 0, 14, 14, 9, 9, 9, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 8, 0, 0], [0, 6, 0, 13, 11, 7, 1, 11, 6, 14, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 1, 14, 0, 7, 13, 7, 6, 6, 0, 6, 0, 0, 6, 1, 0, 14, 6, 14, 6, 11, 6, 1, 0, 14, 6, 6], [6, 0, 0, 10, 7, 10, 12, 14, 12, 12, 12, 12, 12, 13, 6, 7, 7, 10, 0, 0, 0, 0, 6, 10, 0, 10, 0, 10, 0, 10, 14, 13, 0, 0, 13, 14, 14, 12, 13, 0, 10, 12, 13, 6, 13, 6, 12, 12], [0, 12, 11, 12, 5, 5, 5, 16, 16, 11, 16, 16, 5, 11, 11, 16, 0, 16, 11, 11, 0, 0, 0, 0, 5, 16, 11, 5, 5, 12, 11, 11, 5, 12, 11, 11, 0, 11, 0, 16, 16, 0, 12, 0, 0, 0, 5, 5], [0, 0, 2, 2, 0, 0, 11, 2, 0, 0, 11, 5, 0, 0, 5, 10, 9, 9, 9, 9, 9, 9, 9, 6, 11, 5, 6, 9, 9, 0, 6, 0, 10, 9, 9, 9, 0, 9, 10, 6, 0, 6, 11, 9, 6, 11, 0, 0], [4, 4, 7, 5, 4, 4, 7, 7, 0, 7, 0, 11, 11, 0, 4, 0, 11, 7, 0, 0, 4, 11, 11, 4, 0, 0, 4, 4, 4, 4, 4, 4, 4, 11, 4, 7, 4, 4, 4, 11, 0, 4, 0, 11, 0, 0, 11, 4]]
# 1070
# 682.15  секунд
#  7.0 - приспособленность в секунду
# 6341.96 1411.89
# 4930.07

# 2000 5 0.9
# [[0, 0, 8, 9, 0, 0, 5, 1, 0, 8, 11, 10, 0, 0, 13, 12, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 12, 8, 0, 12, 4, 8, 7, 4, 0, 0, 7, 10, 6, 13, 8, 13, 10, 8, 0, 9, 4, 8], [0, 14, 10, 0, 0, 1, 13, 12, 0, 0, 3, 3, 14, 10, 14, 7, 0, 14, 5, 14, 5, 13, 12, 13, 3, 14, 0, 5, 0, 13, 2, 2, 1, 14, 10, 14, 0, 14, 11, 7, 0, 7, 12, 14, 2, 0, 14, 0], [0, 6, 2, 12, 0, 10, 9, 4, 0, 0, 4, 9, 10, 13, 8, 9, 11, 0, 8, 0, 13, 2, 0, 0, 0, 11, 13, 14, 2, 14, 0, 0, 0, 0, 14, 4, 0, 5, 13, 8, 10, 12, 14, 9, 11, 12, 2, 14], [6, 3, 6, 13, 14, 8, 3, 8, 0, 14, 5, 7, 0, 3, 3, 13, 0, 0, 14, 6, 6, 8, 14, 2, 8, 8, 6, 3, 14, 0, 0, 14, 0, 7, 13, 2, 2, 8, 3, 0, 3, 14, 0, 0, 14, 5, 8, 3], [14, 8, 5, 2, 0, 0, 8, 6, 3, 13, 0, 0, 0, 0, 6, 5, 6, 13, 6, 9, 14, 14, 6, 9, 14, 2, 3, 13, 7, 3, 6, 6, 13, 3, 8, 13, 0, 0, 5, 2, 0, 0, 7, 13, 0, 0, 5, 6], [4, 0, 0, 7, 2, 14, 12, 13, 0, 0, 6, 14, 7, 14, 5, 2, 0, 7, 4, 12, 0, 0, 5, 12, 0, 0, 0, 0, 13, 0, 5, 5, 14, 12, 5, 12, 12, 6, 14, 9, 12, 0, 0, 12, 12, 6, 7, 13], [2, 10, 4, 5, 0, 0, 14, 14, 10, 0, 12, 0, 3, 0, 0, 14, 0, 0, 2, 10, 0, 0, 2, 14, 0, 0, 5, 11, 10, 9, 0, 0, 10, 10, 2, 5, 11, 12, 12, 5, 14, 9, 3, 3, 5, 0, 0, 10], [10, 12, 9, 14, 6, 0, 11, 0, 0, 3, 14, 5, 0, 0, 12, 11, 3, 3, 11, 8, 11, 11, 11, 7, 0, 12, 11, 12, 0, 6, 11, 12, 0, 0, 6, 11, 9, 2, 9, 10, 7, 3, 5, 7, 0, 0, 10, 5], [0, 13, 13, 10, 5, 12, 4, 11, 6, 0, 0, 13, 0, 6, 2, 4, 0, 10, 12, 2, 2, 0, 0, 11, 7, 13, 14, 7, 8, 11, 13, 11, 12, 13, 0, 0, 0, 0, 4, 14, 0, 0, 13, 4, 9, 1, 0, 0]]
# 675
# 638.58  секунд
#  8.0 - приспособленность в секунду
# 6333.74 846.32
# 5487.42

# 2000 10 0.9
# [[0, 8, 8, 7, 0, 0, 9, 8, 8, 14, 4, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 9, 9, 7, 0, 0, 14, 7, 0, 8, 7, 0, 0, 13, 0, 0, 4, 8, 8, 8, 7, 8, 14, 13, 13, 13], [13, 9, 0, 0, 0, 0, 2, 12, 13, 10, 2, 7, 0, 0, 2, 7, 0, 0, 14, 13, 14, 14, 0, 0, 0, 0, 10, 14, 0, 0, 14, 13, 0, 10, 14, 12, 0, 2, 1, 2, 14, 2, 1, 1, 12, 10, 7, 14], [10, 14, 11, 12, 0, 2, 11, 13, 0, 0, 14, 9, 0, 5, 13, 4, 0, 14, 5, 9, 0, 9, 14, 4, 12, 9, 14, 13, 11, 11, 2, 9, 0, 0, 4, 2, 11, 14, 14, 4, 0, 0, 12, 10, 0, 0, 2, 10], [0, 3, 13, 3, 0, 0, 13, 6, 0, 3, 8, 13, 0, 0, 0, 0, 3, 0, 0, 6, 3, 0, 0, 14, 0, 0, 13, 8, 0, 0, 8, 14, 0, 3, 13, 5, 3, 0, 0, 5, 0, 0, 13, 14, 3, 14, 0, 0], [0, 0, 1, 13, 3, 8, 7, 5, 11, 13, 13, 11, 0, 0, 5, 8, 14, 6, 2, 8, 0, 0, 7, 6, 6, 13, 1, 6, 7, 14, 2, 7, 0, 0, 7, 9, 13, 8, 9, 3, 6, 13, 0, 0, 3, 6, 0, 0], [0, 6, 12, 10, 12, 7, 12, 1, 0, 0, 10, 1, 6, 7, 14, 5, 0, 2, 4, 2, 0, 0, 12, 5, 10, 12, 4, 1, 5, 8, 6, 2, 0, 5, 12, 14, 0, 0, 7, 7, 0, 5, 14, 4, 0, 0, 8, 9], [0, 16, 14, 14, 0, 14, 14, 14, 3, 0, 0, 5, 0, 16, 16, 14, 0, 0, 0, 0, 0, 3, 3, 11, 3, 2, 0, 0, 0, 0, 10, 5, 5, 0, 2, 0, 14, 11, 11, 10, 10, 16, 10, 5, 10, 16, 9, 1], [3, 11, 7, 5, 6, 9, 0, 0, 12, 6, 0, 0, 10, 2, 6, 3, 11, 11, 10, 14, 11, 0, 0, 13, 0, 0, 6, 10, 3, 3, 13, 11, 2, 7, 5, 11, 0, 0, 12, 14, 2, 7, 5, 9, 0, 0, 12, 8], [0, 0, 4, 4, 11, 10, 4, 11, 6, 0, 7, 0, 2, 10, 11, 11, 0, 0, 6, 10, 0, 11, 11, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 9, 13, 0, 0, 6, 7, 2, 10, 7]]
# 1065
# 973.04  секунд
#  5.0 - приспособленность в секунду
# 6356.94 1182.03
# 5174.91

# 2000 0.1 0.9 без делителей
# [[8, 8, 8, 8, 8, 8, 8, 8, 0, 8, 8, 8, 0, 0, 8, 8, 0, 8, 8, 8, 0, 0, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 8, 8, 8, 8, 8, 8, 0, 0, 8, 8, 0, 0, 8, 8], [0, 0, 14, 14, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0, 14, 14, 0, 14, 14, 14, 14, 14, 14, 14, 0, 14, 14, 14, 0, 14, 14, 14, 0, 14, 14, 14, 0, 0, 14, 14], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [0, 12, 12, 12, 0, 12, 12, 12, 0, 0, 12, 12, 0, 0, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 0, 12, 12, 12, 0, 0, 12, 12, 12, 12, 12, 12, 0, 0, 12, 12, 0, 12, 12, 12], [11, 11, 11, 11, 11, 11, 11, 11, 0, 11, 11, 11, 0, 0, 11, 11, 0, 0, 11, 11, 0, 11, 11, 11, 0, 11, 11, 11, 0, 0, 11, 11, 11, 11, 11, 11, 0, 0, 11, 11, 11, 11, 11, 11, 0, 11, 11, 11], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
# 3180
# 982.23  секунд
#  3.0 - приспособленность в секунду
# 6334.08 3182.26
# 3151.8199999999997

# 2000 6, 0.9, изменил скрещивание
# [[4, 4, 4, 5, 8, 12, 4, 10, 0, 0, 8, 8, 0, 2, 12, 12, 2, 12, 0, 0, 0, 8, 4, 8, 0, 14, 8, 4, 0, 0, 8, 12, 2, 5, 5, 5, 0, 0, 8, 12, 0, 10, 2, 4, 4, 4, 4, 4], [10, 13, 14, 3, 13, 9, 3, 14, 0, 0, 14, 3, 14, 0, 0, 14, 0, 0, 6, 14, 0, 14, 8, 10, 14, 0, 0, 3, 5, 0, 0, 14, 10, 6, 13, 10, 10, 13, 13, 5, 0, 0, 0, 0, 0, 0, 6, 6], [2, 12, 12, 12, 0, 0, 9, 12, 5, 5, 4, 12, 2, 7, 14, 7, 0, 0, 12, 9, 0, 0, 3, 12, 0, 13, 14, 5, 0, 7, 14, 8, 0, 0, 9, 14, 0, 5, 2, 4, 0, 12, 13, 12, 2, 2, 14, 2], [0, 14, 1, 13, 3, 2, 11, 13, 2, 3, 7, 11, 7, 14, 5, 9, 0, 1, 2, 5, 14, 0, 0, 5, 0, 0, 13, 6, 1, 14, 5, 6, 0, 14, 14, 13, 9, 0, 9, 0, 7, 9, 14, 2, 0, 13, 5, 11], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 2, 0, 6, 4, 2, 2, 13, 0, 0, 0, 11, 7, 8, 7, 13, 6, 2, 0, 13, 7, 6, 0, 9, 0, 13, 0, 6, 9, 8, 0, 6, 1, 13], [7, 7, 6, 7, 0, 0, 6, 7, 10, 14, 13, 7, 0, 0, 13, 13, 0, 13, 14, 7, 0, 7, 7, 14, 6, 7, 12, 10, 0, 8, 13, 10, 0, 0, 8, 12, 7, 14, 5, 7, 14, 0, 0, 7, 0, 9, 12, 5], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 10, 5, 9, 11, 11, 10, 14, 3, 3, 5, 0, 0, 0, 0, 2, 9, 14, 0, 11, 0, 0, 10, 14, 9, 0, 14, 0, 14, 0, 14, 11, 12], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 0, 11, 13, 11, 10, 13, 7, 1, 13, 6, 0, 2, 3, 13, 11, 10, 11, 13, 0, 11, 3, 0, 0, 2, 6, 2, 11, 2, 6, 11, 7, 11, 0, 0], [14, 5, 0, 0, 0, 0, 13, 2, 0, 6, 11, 4, 10, 11, 10, 4, 6, 0, 13, 0, 5, 12, 9, 13, 10, 0, 10, 0, 0, 2, 4, 4, 6, 0, 0, 2, 13, 6, 11, 11, 0, 0, 11, 5, 11, 0, 0, 14]]
# 1105
# 790.58  секунд
#  6.0 - приспособленность в секунду
# 6327.98 1175.4
# 5152.58

# 2000 4 0.9
# [[0, 0, 12, 7, 12, 12, 7, 12, 2, 0, 0, 8, 0, 12, 2, 8, 0, 0, 4, 10, 12, 4, 8, 8, 0, 0, 8, 8, 0, 0, 8, 9, 10, 8, 4, 4, 0, 4, 0, 4, 7, 7, 10, 2, 2, 2, 10, 4], [1, 0, 13, 0, 0, 8, 10, 13, 0, 8, 10, 13, 5, 2, 14, 6, 14, 0, 14, 0, 8, 14, 1, 13, 1, 0, 13, 0, 0, 0, 7, 7, 1, 10, 1, 13, 13, 1, 2, 13, 0, 0, 13, 10, 6, 8, 8, 13], [0, 4, 4, 14, 0, 0, 4, 8, 14, 11, 13, 14, 14, 14, 12, 9, 0, 13, 8, 4, 0, 0, 12, 14, 0, 0, 7, 12, 0, 8, 4, 8, 0, 0, 14, 8, 14, 14, 7, 7, 14, 13, 12, 4, 0, 14, 9, 7], [5, 0, 0, 3, 2, 14, 2, 5, 0, 2, 3, 3, 3, 8, 5, 14, 0, 14, 9, 13, 13, 0, 14, 0, 8, 14, 2, 13, 0, 0, 14, 2, 0, 14, 5, 9, 0, 0, 14, 2, 0, 8, 14, 14, 13, 5, 3, 2], [7, 6, 8, 8, 0, 3, 13, 6, 0, 6, 8, 0, 0, 11, 6, 11, 3, 3, 6, 8, 7, 13, 13, 9, 0, 6, 11, 2, 2, 0, 9, 0, 0, 13, 7, 11, 6, 8, 11, 11, 11, 9, 0, 0, 8, 9, 7, 8], [14, 0, 2, 0, 7, 7, 14, 14, 6, 12, 0, 6, 0, 6, 0, 1, 0, 6, 2, 2, 1, 12, 6, 7, 0, 0, 12, 7, 14, 6, 2, 14, 0, 7, 12, 2, 0, 7, 12, 12, 12, 14, 0, 12, 0, 7, 12, 12], [0, 0, 11, 9, 0, 0, 5, 11, 0, 16, 14, 11, 0, 0, 10, 16, 0, 5, 11, 14, 14, 5, 5, 3, 14, 3, 5, 14, 0, 14, 5, 10, 0, 5, 0, 14, 0, 0, 5, 14, 5, 5, 9, 5, 0, 11, 14, 14], [0, 3, 5, 5, 11, 5, 12, 2, 0, 0, 12, 5, 11, 5, 13, 5, 11, 0, 5, 0, 0, 11, 11, 12, 11, 5, 14, 0, 11, 3, 11, 5, 0, 2, 11, 12, 11, 11, 0, 0, 3, 3, 2, 0, 14, 0, 0, 11], [0, 11, 9, 11, 0, 11, 0, 4, 11, 13, 7, 12, 0, 0, 0, 0, 0, 11, 12, 7, 0, 0, 9, 11, 0, 13, 9, 11, 0, 0, 13, 12, 0, 0, 13, 7, 4, 13, 4, 0, 0, 0, 7, 7, 11, 4, 4, 0]]
# 575
# 613.63  секунд
#  9.0 - приспособленность в секунду
# 6358.22 691.3
# 5666.92

# 2000 4 0.9
# [[4, 4, 8, 8, 0, 4, 10, 5, 0, 10, 8, 8, 0, 2, 8, 10, 0, 2, 8, 2, 0, 0, 2, 4, 8, 5, 0, 0, 0, 0, 8, 8, 0, 4, 8, 8, 4, 8, 2, 8, 4, 5, 5, 8, 0, 10, 5, 5], [14, 14, 14, 14, 14, 14, 14, 14, 0, 14, 14, 14, 0, 0, 14, 14, 14, 0, 0, 14, 0, 14, 14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 14, 7, 14, 7, 7, 14, 14, 2, 0, 7, 2, 14, 14, 14, 0, 14], [11, 11, 11, 11, 11, 11, 0, 0, 0, 13, 13, 13, 14, 13, 13, 9, 0, 9, 14, 13, 5, 13, 0, 0, 0, 8, 13, 14, 0, 8, 9, 14, 0, 0, 11, 14, 8, 9, 0, 0, 12, 12, 12, 13, 12, 12, 8, 4], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 13, 11, 0, 0, 8, 13, 11, 11, 0, 0, 0, 8, 6, 8], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 6, 2, 6, 0, 11, 7, 11, 6, 2, 11, 6, 0, 11, 6, 6, 0, 2, 6, 0, 3, 3, 7, 7, 0, 0, 9, 3, 0, 7, 2, 7], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 0, 12, 12, 12, 0, 0, 10, 12, 0, 0, 0, 0], [0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 10, 2, 2, 14, 0, 0, 11, 5, 11, 5, 0, 11, 2, 10, 0, 2, 14, 11, 10, 5, 2, 2, 11, 11, 0, 11, 14, 16, 0, 0, 0, 2, 9, 2], [7, 7, 7, 7, 0, 7, 7, 7, 7, 5, 5, 7, 0, 0, 7, 5, 0, 11, 11, 8, 0, 0, 12, 7, 0, 12, 5, 5, 7, 5, 11, 5, 7, 12, 5, 5, 0, 0, 5, 5, 0, 2, 13, 7, 0, 0, 12, 11], [0, 13, 13, 13, 0, 13, 13, 11, 0, 0, 11, 11, 11, 10, 4, 7, 13, 4, 6, 11, 4, 7, 0, 0, 10, 0, 14, 0, 0, 7, 13, 13, 4, 11, 4, 13, 0, 6, 11, 4, 7, 13, 7, 10, 0, 0, 14, 13]]
# 1755
# 642.18  секунд
#  7.0 - приспособленность в секунду
# 6323.58 1786.78
# 4536.8

# 2000 4 0.9
# [[0, 8, 9, 4, 9, 13, 0, 0, 0, 8, 5, 8, 5, 8, 4, 4, 0, 4, 4, 8, 0, 13, 4, 8, 4, 4, 5, 8, 0, 0, 13, 4, 0, 4, 4, 13, 13, 5, 13, 4, 5, 0, 8, 0, 0, 8, 4, 4], [0, 13, 14, 3, 0, 8, 7, 7, 8, 7, 7, 14, 0, 0, 5, 5, 0, 0, 5, 5, 7, 14, 5, 5, 0, 13, 13, 13, 3, 0, 0, 5, 0, 3, 5, 14, 3, 7, 14, 13, 3, 0, 13, 0, 4, 3, 13, 3], [0, 5, 12, 8, 13, 14, 14, 9, 4, 4, 9, 9, 0, 0, 9, 13, 0, 8, 14, 9, 3, 0, 0, 4, 0, 0, 9, 4, 0, 12, 14, 14, 0, 14, 8, 4, 0, 8, 9, 9, 0, 3, 4, 5, 8, 13, 12, 5], [14, 9, 8, 14, 0, 0, 8, 14, 14, 9, 14, 0, 0, 14, 8, 8, 2, 14, 0, 0, 14, 8, 2, 14, 0, 8, 8, 14, 9, 11, 8, 8, 11, 8, 0, 0, 9, 0, 0, 2, 0, 8, 2, 2, 14, 9, 8, 11], [6, 6, 6, 6, 0, 0, 0, 0, 5, 13, 3, 13, 13, 3, 13, 1, 0, 0, 9, 6, 13, 3, 9, 1, 9, 6, 7, 5, 7, 3, 6, 13, 7, 6, 13, 7, 0, 0, 7, 5, 0, 0, 6, 6, 0, 0, 6, 9], [2, 2, 13, 13, 0, 0, 12, 13, 6, 0, 0, 12, 12, 12, 12, 12, 13, 5, 6, 13, 0, 0, 12, 13, 13, 2, 12, 2, 0, 0, 12, 12, 12, 13, 12, 2, 0, 0, 0, 0, 12, 6, 12, 12, 12, 5, 5, 13], [5, 11, 2, 11, 0, 0, 0, 0, 0, 5, 11, 5, 0, 5, 14, 14, 5, 11, 12, 12, 5, 11, 10, 11, 0, 0, 11, 12, 5, 14, 5, 11, 0, 12, 10, 11, 0, 11, 5, 10, 10, 0, 5, 15, 5, 14, 2, 12], [0, 0, 0, 0, 6, 6, 11, 3, 3, 11, 0, 3, 6, 6, 3, 9, 0, 9, 10, 11, 9, 9, 0, 9, 10, 11, 3, 11, 0, 0, 10, 3, 3, 0, 9, 0, 0, 3, 11, 6, 6, 11, 10, 9, 0, 0, 11, 6], [0, 0, 0, 0, 10, 5, 2, 5, 10, 2, 0, 10, 2, 10, 10, 6, 10, 2, 2, 2, 0, 0, 6, 6, 0, 0, 14, 7, 10, 7, 2, 7, 0, 10, 2, 5, 6, 0, 0, 14, 0, 0, 14, 10, 2, 10, 9, 8]]
# 590
# 567.17  секунд
#  9.0 - приспособленность в секунду
# 6326.4 658.94
# 5667.459999999999

# 10000 4 0.9
# [[10, 12, 11, 10, 8, 4, 13, 9, 0, 0, 9, 12, 2, 7, 8, 7, 0, 0, 10, 11, 0, 0, 4, 4, 0, 0, 9, 9, 2, 11, 12, 8, 2, 0, 0, 8, 12, 2, 8, 8, 0, 9, 9, 8, 0, 5, 13, 7], [14, 8, 0, 0, 0, 14, 12, 2, 2, 1, 10, 13, 10, 13, 14, 14, 0, 0, 3, 5, 0, 7, 12, 14, 0, 13, 7, 7, 0, 0, 13, 6, 8, 12, 8, 13, 0, 14, 6, 1, 2, 2, 1, 10, 0, 0, 5, 12], [0, 11, 13, 4, 14, 2, 14, 5, 0, 8, 14, 11, 0, 14, 9, 10, 0, 0, 4, 9, 0, 11, 14, 2, 0, 9, 5, 12, 0, 14, 5, 2, 10, 14, 11, 9, 13, 13, 5, 5, 0, 0, 8, 14, 0, 0, 9, 8], [3, 0, 0, 2, 0, 8, 11, 6, 0, 5, 8, 8, 13, 8, 13, 13, 14, 14, 14, 14, 0, 0, 13, 5, 8, 2, 8, 3, 0, 6, 8, 14, 0, 0, 13, 14, 1, 0, 0, 13, 0, 13, 11, 1, 14, 13, 6, 13], [0, 13, 2, 8, 6, 6, 0, 0, 0, 6, 1, 6, 6, 0, 6, 0, 13, 6, 8, 6, 11, 8, 6, 6, 1, 0, 13, 0, 11, 2, 2, 5, 13, 13, 14, 6, 6, 6, 13, 6, 0, 0, 0, 0, 6, 2, 2, 14], [0, 0, 4, 12, 0, 0, 4, 10, 4, 12, 13, 14, 0, 0, 5, 4, 10, 1, 6, 12, 8, 14, 8, 8, 12, 10, 14, 4, 0, 0, 0, 0, 0, 4, 4, 1, 8, 12, 4, 4, 0, 4, 13, 5, 5, 4, 12, 1], [0, 0, 9, 9, 0, 9, 2, 16, 0, 16, 16, 5, 12, 3, 2, 9, 12, 10, 9, 2, 14, 0, 0, 9, 0, 0, 2, 14, 0, 12, 14, 12, 0, 9, 2, 5, 0, 0, 3, 14, 9, 14, 16, 16, 10, 9, 14, 16], [0, 6, 7, 5, 0, 5, 5, 12, 10, 0, 0, 3, 5, 11, 10, 3, 0, 5, 12, 0, 6, 5, 5, 12, 6, 6, 10, 11, 0, 0, 6, 10, 7, 6, 12, 11, 0, 0, 9, 10, 0, 11, 12, 7, 0, 11, 11, 9], [12, 2, 14, 7, 0, 10, 7, 13, 6, 11, 7, 4, 0, 0, 12, 12, 0, 0, 13, 13, 0, 2, 11, 10, 0, 0, 4, 13, 13, 13, 4, 13, 14, 11, 6, 12, 11, 11, 10, 12, 11, 6, 0, 0, 0, 0, 4, 11]]
# 320
# 3020.48  секунд
#  1.0 - приспособленность в секунду
# 6372.9 388.17
# 5984.73

# 2000 0.1 0.9 новая мутация
# [[6, 0, 0, 6, 6, 13, 5, 3, 3, 5, 3, 6, 5, 0, 7, 5, 13, 11, 0, 0, 13, 11, 0, 0, 5, 7, 0, 3, 13, 0, 0, 3, 13, 0, 6, 3, 0, 0, 3, 11, 11, 0, 3, 3, 3, 0, 0, 6], [0, 9, 9, 9, 8, 8, 0, 4, 8, 0, 4, 0, 0, 4, 10, 10, 0, 0, 4, 8, 0, 0, 4, 8, 8, 10, 0, 0, 0, 0, 0, 0, 10, 4, 9, 9, 0, 0, 8, 8, 8, 4, 8, 4, 4, 0, 9, 0], [0, 12, 0, 12, 12, 12, 12, 12, 12, 12, 0, 2, 0, 12, 8, 2, 12, 8, 8, 2, 2, 12, 8, 12, 8, 8, 6, 5, 12, 6, 5, 5, 5, 0, 6, 12, 0, 6, 5, 6, 5, 12, 12, 0, 12, 0, 0, 5], [0, 7, 11, 11, 11, 10, 10, 7, 11, 10, 7, 0, 3, 11, 12, 12, 10, 0, 12, 12, 10, 5, 5, 10, 10, 3, 14, 11, 7, 12, 7, 7, 3, 0, 11, 11, 0, 0, 0, 0, 0, 0, 14, 7, 0, 14, 7, 0], [0, 14, 6, 8, 14, 0, 14, 0, 6, 8, 14, 14, 0, 14, 3, 3, 0, 2, 10, 0, 0, 0, 13, 13, 2, 0, 13, 3, 0, 0, 0, 12, 12, 0, 8, 0, 0, 10, 6, 12, 14, 14, 8, 14, 0, 0, 14, 2], [0, 0, 14, 14, 4, 0, 0, 11, 11, 4, 12, 0, 5, 11, 4, 4, 5, 14, 0, 0, 4, 12, 0, 0, 13, 4, 5, 0, 0, 8, 4, 4, 4, 11, 12, 4, 0, 0, 14, 14, 0, 8, 0, 12, 11, 13, 0, 2], [5, 11, 3, 2, 9, 9, 0, 0, 2, 9, 0, 11, 0, 0, 1, 8, 0, 14, 5, 5, 11, 14, 0, 0, 1, 2, 8, 14, 0, 0, 10, 3, 11, 11, 0, 0, 11, 14, 10, 9, 9, 0, 14, 2, 5, 0, 15, 11], [0, 0, 8, 1, 0, 0, 2, 8, 1, 2, 0, 0, 6, 13, 0, 0, 2, 0, 2, 14, 12, 2, 1, 14, 6, 0, 1, 0, 2, 0, 2, 0, 9, 13, 0, 0, 0, 9, 14, 2, 6, 0, 0, 8, 13, 1, 0, 8], [11, 14, 0, 7, 0, 6, 6, 14, 14, 0, 7, 0, 0, 0, 13, 13, 0, 0, 11, 11, 7, 0, 6, 6, 0, 13, 7, 9, 2, 11, 0, 0, 0, 2, 0, 14, 0, 0, 0, 0, 0, 9, 7, 7, 7, 7, 10, 11]]
# 3120
# 256.59  секунд
#  11.0 - приспособленность в секунду
# 6354.16 3320.99
# 3033.17

# 2000 0.5 0.9 новая мутация
# [[6, 6, 11, 0, 9, 5, 0, 11, 0, 7, 11, 11, 0, 0, 11, 11, 0, 10, 14, 0, 14, 0, 12, 14, 10, 0, 0, 13, 10, 12, 5, 0, 0, 0, 0, 6, 7, 9, 9, 7, 9, 9, 13, 0, 12, 5, 1, 6], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 12, 0, 11, 8, 8, 12, 8, 0, 2, 9, 13, 8, 12, 13, 8, 2, 14, 0, 13, 8, 5, 0, 8, 2, 5, 5, 8, 13, 9, 0, 0, 0, 14, 13], [16, 10, 5, 11, 5, 12, 2, 12, 11, 0, 11, 5, 5, 0, 0, 14, 0, 0, 12, 11, 16, 3, 0, 9, 0, 14, 11, 0, 0, 0, 10, 9, 9, 9, 9, 8, 14, 3, 0, 10, 10, 5, 5, 2, 11, 11, 13, 0], [10, 0, 2, 14, 13, 0, 7, 0, 0, 0, 14, 10, 13, 10, 14, 2, 8, 6, 0, 13, 3, 13, 8, 3, 14, 0, 0, 12, 0, 12, 8, 6, 0, 6, 0, 13, 2, 7, 0, 0, 0, 0, 7, 4, 0, 12, 5, 6], [13, 13, 13, 13, 13, 13, 0, 0, 0, 13, 2, 0, 0, 0, 0, 0, 14, 14, 14, 0, 13, 8, 14, 0, 0, 14, 2, 2, 13, 8, 12, 14, 14, 14, 14, 0, 0, 13, 13, 13, 14, 8, 8, 12, 0, 14, 8, 0], [14, 1, 0, 0, 2, 3, 0, 14, 0, 14, 6, 14, 6, 2, 11, 11, 3, 0, 0, 7, 6, 0, 0, 11, 7, 1, 14, 9, 14, 13, 13, 2, 7, 12, 12, 3, 2, 0, 7, 0, 7, 0, 0, 13, 6, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 11, 7, 7, 0, 0, 4, 12, 4, 0, 7, 0, 14, 0, 4, 14, 0, 4, 10, 9, 0, 10, 2, 11, 11, 11, 11, 14, 6, 5, 0], [6, 6, 6, 6, 6, 0, 5, 5, 6, 0, 12, 0, 5, 6, 6, 6, 4, 0, 0, 2, 12, 7, 1, 12, 0, 2, 7, 11, 2, 0, 4, 0, 11, 0, 11, 14, 12, 11, 14, 0, 0, 1, 6, 7, 2, 2, 0, 10], [12, 12, 12, 2, 12, 14, 14, 4, 14, 4, 14, 10, 0, 0, 0, 0, 12, 4, 11, 13, 0, 0, 0, 0, 2, 11, 4, 0, 10, 5, 6, 0, 0, 10, 3, 0, 13, 14, 4, 0, 13, 14, 4, 11, 14, 14, 0, 12]]
# 3500
# 362.51  секунд
#  7.0 - приспособленность в секунду
# 6331.42 3697.13
# 2634.29

# 2000 4 0.9 новая мутация ужасна
# [[5, 11, 11, 6, 12, 0, 6, 0, 5, 0, 9, 11, 0, 9, 11, 9, 8, 0, 8, 0, 0, 2, 2, 0, 12, 0, 12, 0, 3, 12, 0, 0, 0, 2, 13, 10, 0, 2, 5, 11, 3, 8, 13, 0, 0, 0, 0, 0], [6, 6, 6, 6, 6, 0, 13, 0, 7, 9, 7, 0, 12, 6, 0, 13, 0, 7, 9, 7, 2, 13, 6, 0, 13, 7, 13, 2, 0, 0, 0, 0, 0, 0, 0, 9, 11, 7, 0, 0, 6, 6, 11, 0, 6, 6, 2, 0], [13, 13, 7, 6, 0, 0, 14, 8, 0, 2, 8, 6, 7, 3, 0, 3, 0, 0, 0, 3, 0, 0, 14, 3, 14, 3, 0, 13, 0, 7, 14, 14, 2, 7, 0, 14, 1, 0, 8, 0, 0, 5, 6, 13, 0, 14, 0, 13], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 9, 0, 0, 0, 2, 13, 0, 8, 12, 9, 0, 0, 0, 0, 7, 2, 14, 0, 9, 12, 7, 14, 14, 13, 0, 13, 0, 5], [12, 12, 12, 8, 8, 0, 0, 13, 2, 9, 12, 8, 0, 10, 8, 0, 8, 8, 0, 8, 0, 8, 0, 13, 2, 9, 0, 0, 10, 0, 0, 10, 13, 13, 12, 9, 12, 11, 4, 13, 4, 11, 2, 0, 0, 8, 12, 12], [10, 3, 11, 0, 11, 14, 0, 11, 14, 12, 2, 14, 3, 0, 0, 14, 0, 3, 0, 0, 14, 0, 0, 14, 16, 12, 3, 0, 9, 0, 10, 11, 10, 11, 14, 2, 0, 9, 10, 2, 14, 5, 0, 16, 3, 0, 0, 14], [14, 14, 5, 2, 0, 7, 12, 14, 10, 0, 5, 2, 0, 5, 10, 0, 1, 5, 2, 0, 5, 0, 12, 8, 8, 4, 8, 12, 0, 0, 7, 0, 10, 8, 2, 4, 12, 5, 6, 7, 11, 12, 0, 0, 12, 0, 4, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 13, 4, 14, 0, 5, 10, 0, 5, 10, 11, 10, 11, 11, 11, 12, 12, 13, 11, 7, 0, 6, 0, 13, 0, 7, 12, 0, 0, 0, 9, 10, 7, 11, 14, 0, 10], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 12, 0, 12, 0, 14, 14, 0, 0, 14, 14, 6, 0, 14, 3, 0, 0, 12, 14, 0, 3, 14, 0, 14, 3, 0, 0, 0, 0, 6, 6]]
# 4230
# 805.9  секунд
#  2.0 - приспособленность в секунду
# 6362.06 4430.52
# 1931.54

# 2000 4 0.9
# [[0, 0, 8, 8, 13, 5, 8, 13, 0, 0, 2, 8, 0, 0, 13, 5, 8, 8, 10, 13, 10, 2, 8, 8, 0, 0, 8, 10, 2, 8, 8, 8, 0, 8, 13, 13, 0, 10, 8, 5, 0, 8, 6, 2, 0, 13, 10, 13], [14, 7, 14, 14, 14, 0, 14, 14, 14, 14, 14, 0, 2, 14, 0, 0, 7, 14, 0, 14, 0, 14, 14, 2, 14, 14, 14, 7, 0, 0, 14, 2, 0, 0, 7, 12, 0, 0, 0, 0, 7, 0, 0, 5, 14, 1, 5, 14], [0, 0, 12, 12, 0, 12, 12, 12, 0, 12, 10, 14, 0, 12, 12, 9, 9, 12, 14, 9, 12, 9, 9, 0, 9, 12, 0, 12, 0, 0, 12, 14, 12, 9, 14, 9, 12, 12, 14, 12, 0, 12, 14, 14, 11, 10, 0, 0], [13, 2, 9, 9, 9, 7, 2, 6, 13, 2, 9, 2, 0, 0, 14, 14, 14, 0, 2, 0, 0, 0, 13, 13, 0, 0, 7, 14, 9, 14, 9, 13, 0, 14, 0, 14, 6, 6, 2, 2, 14, 14, 0, 0, 2, 14, 14, 6], [0, 11, 13, 13, 0, 0, 6, 2, 2, 6, 6, 6, 0, 0, 11, 6, 0, 11, 13, 8, 6, 6, 6, 11, 0, 13, 11, 9, 13, 9, 2, 6, 2, 11, 0, 0, 2, 8, 13, 8, 0, 5, 11, 13, 0, 0, 8, 9], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 5, 2, 12, 13, 5, 12, 12, 5, 12, 5, 12, 0, 0, 12, 5, 0, 5, 5, 12, 5, 5, 5, 5, 10, 5, 10, 13, 0, 0, 2, 12, 13, 12, 2, 0], [0, 14, 5, 2, 0, 14, 11, 5, 11, 11, 12, 5, 14, 2, 0, 0, 0, 0, 5, 2, 14, 11, 12, 14, 11, 0, 5, 0, 14, 12, 11, 11, 14, 12, 2, 2, 14, 14, 5, 14, 11, 11, 0, 0, 0, 0, 7, 5], [3, 12, 7, 6, 0, 0, 0, 0, 9, 13, 0, 0, 13, 6, 9, 3, 0, 0, 0, 0, 0, 0, 2, 9, 3, 9, 9, 2, 0, 6, 6, 0, 0, 6, 9, 6, 13, 9, 0, 0, 3, 3, 13, 7, 0, 0, 13, 12], [7, 5, 11, 11, 4, 11, 5, 4, 7, 4, 0, 0, 0, 0, 7, 11, 0, 7, 7, 11, 0, 4, 11, 7, 4, 4, 0, 0, 7, 10, 4, 5, 0, 0, 4, 10, 5, 4, 7, 11, 0, 0, 4, 10, 7, 5, 4, 11]]
# 805
# 533.53  секунд
#  10.0 - приспособленность в секунду
# 6337.56 890.76
# 5446.8
# 2000
# [[0, 0, 8, 8, 13, 5, 8, 13, 0, 0, 2, 8, 0, 0, 13, 8, 8, 8, 10, 13, 10, 2, 8, 8, 0, 0, 8, 13, 2, 8, 8, 8, 0, 8, 10, 13, 0, 10, 8, 5, 0, 8, 6, 2, 0, 13, 10, 13], [14, 7, 14, 14, 14, 0, 14, 14, 14, 14, 14, 0, 2, 14, 0, 0, 7, 14, 0, 14, 0, 14, 14, 2, 14, 14, 14, 7, 0, 0, 14, 2, 0, 0, 7, 12, 0, 0, 0, 0, 7, 0, 0, 5, 14, 1, 5, 14], [0, 0, 12, 12, 0, 12, 12, 12, 0, 12, 10, 14, 0, 12, 12, 9, 9, 12, 14, 9, 12, 9, 9, 0, 9, 12, 0, 12, 0, 0, 12, 14, 12, 9, 14, 9, 12, 12, 14, 12, 0, 12, 14, 14, 11, 10, 0, 0], [13, 2, 9, 9, 9, 7, 2, 6, 13, 2, 9, 2, 0, 0, 14, 14, 14, 0, 2, 0, 0, 0, 13, 13, 0, 0, 7, 14, 0, 14, 9, 13, 0, 14, 13, 14, 6, 6, 2, 2, 14, 14, 0, 0, 2, 14, 14, 6], [0, 11, 13, 13, 0, 0, 6, 2, 2, 6, 6, 6, 0, 0, 11, 6, 0, 11, 13, 8, 6, 6, 6, 11, 0, 11, 11, 9, 13, 9, 2, 6, 2, 11, 0, 0, 2, 8, 13, 8, 0, 5, 11, 13, 0, 0, 8, 9], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 5, 2, 12, 12, 5, 12, 12, 5, 12, 5, 12, 0, 0, 12, 5, 0, 5, 5, 12, 5, 5, 5, 5, 10, 5, 10, 13, 0, 0, 2, 12, 13, 12, 12, 2], [0, 14, 5, 2, 0, 14, 11, 5, 11, 11, 12, 5, 14, 2, 0, 0, 0, 0, 5, 2, 14, 11, 12, 14, 0, 0, 5, 11, 14, 12, 11, 11, 14, 12, 2, 2, 14, 14, 5, 14, 11, 11, 0, 0, 0, 0, 7, 5], [3, 12, 7, 6, 0, 0, 0, 0, 9, 13, 13, 9, 13, 6, 9, 3, 0, 0, 0, 0, 9, 13, 2, 9, 3, 9, 9, 2, 0, 6, 6, 9, 0, 6, 9, 6, 13, 9, 0, 0, 3, 3, 12, 7, 0, 0, 13, 12], [7, 5, 11, 11, 4, 11, 5, 4, 7, 4, 0, 0, 0, 0, 7, 11, 0, 7, 7, 11, 0, 4, 11, 7, 4, 4, 0, 0, 7, 11, 4, 5, 0, 0, 4, 10, 5, 4, 7, 11, 0, 0, 4, 10, 7, 5, 4, 11]]
# 685
# 824.51  секунд
#  0.0 - приспособленность в секунду
# 890.76 753.53
# 137.23000000000002
# 2000
# [[0, 0, 8, 8, 13, 5, 8, 13, 0, 0, 2, 8, 0, 0, 13, 8, 8, 8, 8, 13, 10, 2, 8, 8, 0, 2, 8, 13, 0, 8, 8, 8, 0, 8, 10, 13, 0, 10, 8, 5, 0, 8, 6, 2, 0, 13, 10, 8], [14, 7, 14, 14, 14, 0, 14, 14, 14, 14, 14, 0, 2, 14, 0, 0, 7, 14, 0, 14, 0, 14, 14, 2, 14, 14, 14, 7, 0, 0, 14, 2, 0, 0, 7, 12, 0, 0, 0, 0, 7, 0, 0, 5, 14, 1, 5, 14], [0, 0, 12, 12, 0, 12, 12, 12, 0, 12, 10, 14, 0, 12, 12, 9, 9, 12, 14, 9, 12, 9, 9, 0, 9, 12, 0, 12, 0, 0, 12, 14, 12, 9, 14, 9, 12, 12, 14, 12, 0, 12, 14, 14, 11, 10, 0, 0], [13, 2, 9, 9, 9, 7, 2, 6, 13, 2, 9, 2, 0, 0, 14, 14, 14, 0, 2, 0, 0, 0, 13, 13, 0, 0, 7, 14, 0, 14, 9, 13, 0, 14, 13, 14, 6, 6, 2, 2, 14, 14, 0, 0, 2, 14, 14, 6], [0, 13, 13, 13, 0, 0, 6, 2, 2, 6, 6, 6, 0, 0, 11, 6, 0, 11, 13, 8, 6, 6, 6, 11, 0, 11, 11, 9, 13, 9, 2, 6, 2, 11, 0, 0, 2, 8, 13, 8, 0, 5, 11, 13, 0, 0, 8, 9], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 5, 2, 12, 12, 5, 12, 12, 5, 12, 5, 12, 0, 0, 12, 5, 0, 5, 5, 12, 5, 5, 5, 5, 0, 5, 10, 13, 0, 0, 2, 12, 5, 12, 12, 2], [0, 14, 5, 2, 0, 14, 11, 5, 11, 11, 12, 5, 14, 2, 0, 0, 0, 0, 5, 2, 14, 11, 12, 14, 0, 0, 5, 11, 14, 12, 11, 11, 14, 12, 2, 2, 14, 14, 5, 14, 11, 11, 0, 0, 0, 0, 7, 5], [3, 12, 7, 6, 0, 0, 0, 0, 9, 13, 13, 9, 13, 6, 9, 3, 0, 0, 0, 0, 9, 13, 2, 9, 3, 9, 9, 2, 0, 0, 6, 9, 0, 0, 9, 6, 13, 9, 6, 9, 3, 3, 13, 7, 0, 0, 13, 12], [7, 5, 11, 11, 4, 11, 5, 4, 7, 4, 0, 0, 0, 0, 7, 11, 0, 7, 7, 11, 0, 4, 10, 7, 4, 4, 0, 0, 7, 11, 4, 5, 0, 0, 4, 10, 5, 4, 4, 11, 0, 0, 4, 11, 7, 4, 4, 11]]
# 660
# 674.44  секунд
#  0.0 - приспособленность в секунду
# 753.53 747.38
# 6.149999999999977

# 2000 3.5
# [[13, 2, 13, 5, 0, 5, 5, 8, 0, 4, 4, 4, 0, 0, 9, 2, 8, 13, 9, 2, 8, 13, 0, 0, 2, 4, 9, 5, 0, 8, 8, 5, 8, 8, 13, 9, 8, 2, 0, 0, 0, 4, 8, 12, 8, 0, 2, 0], [0, 14, 0, 13, 1, 3, 13, 12, 0, 14, 12, 8, 1, 1, 12, 13, 0, 0, 1, 14, 0, 2, 13, 3, 0, 1, 13, 3, 14, 13, 3, 12, 0, 1, 3, 12, 0, 0, 8, 8, 0, 0, 3, 1, 7, 14, 14, 2], [0, 0, 9, 12, 9, 0, 8, 0, 0, 11, 9, 2, 0, 11, 5, 8, 14, 11, 11, 11, 2, 14, 11, 12, 0, 5, 14, 9, 4, 14, 9, 14, 2, 14, 11, 11, 4, 0, 0, 11, 0, 9, 14, 14, 5, 8, 0, 0], [0, 7, 14, 1, 0, 0, 14, 9, 14, 13, 5, 9, 13, 13, 8, 6, 6, 0, 8, 0, 0, 8, 8, 9, 0, 0, 8, 13, 7, 5, 13, 13, 14, 6, 14, 8, 14, 0, 0, 1, 0, 14, 5, 9, 14, 13, 0, 7], [11, 0, 0, 14, 7, 13, 3, 3, 7, 8, 11, 11, 0, 0, 3, 5, 5, 8, 13, 13, 0, 0, 5, 7, 6, 6, 6, 8, 0, 0, 14, 8, 0, 0, 7, 6, 0, 0, 14, 14, 11, 8, 13, 5, 13, 6, 11, 8], [0, 0, 8, 8, 8, 0, 0, 5, 0, 12, 13, 13, 0, 12, 14, 10, 12, 5, 12, 5, 10, 12, 12, 5, 0, 12, 12, 14, 8, 12, 12, 0, 0, 0, 5, 2, 2, 10, 12, 12, 0, 2, 0, 8, 10, 5, 5, 5], [0, 0, 2, 9, 16, 16, 16, 14, 0, 0, 0, 0, 14, 16, 16, 14, 16, 16, 14, 9, 16, 9, 14, 14, 14, 14, 0, 0, 0, 16, 16, 2, 16, 16, 16, 16, 0, 16, 16, 16, 0, 0, 11, 11, 3, 16, 9, 14], [0, 10, 11, 7, 0, 0, 11, 13, 11, 6, 14, 7, 0, 0, 7, 12, 0, 2, 6, 7, 12, 7, 9, 13, 11, 0, 11, 0, 2, 7, 11, 6, 0, 0, 0, 0, 11, 7, 11, 9, 14, 10, 12, 7, 0, 0, 12, 12], [2, 4, 4, 10, 11, 11, 6, 11, 0, 2, 2, 14, 0, 0, 10, 4, 0, 14, 4, 4, 6, 0, 2, 0, 4, 10, 2, 11, 0, 10, 6, 11, 10, 11, 0, 14, 0, 14, 2, 6, 2, 0, 6, 0, 0, 10, 6, 11]]
# 490
# 535.77  секунд
#  10.0 - приспособленность в секунду
# 6337.86 609.66
# 5728.2

# 2000 3.5
# [[7, 8, 10, 8, 2, 8, 14, 11, 0, 10, 8, 9, 14, 0, 0, 9, 12, 0, 11, 0, 13, 12, 10, 4, 12, 0, 0, 10, 7, 8, 8, 4, 0, 13, 13, 2, 2, 8, 4, 7, 13, 8, 9, 4, 0, 4, 9, 4], [0, 13, 13, 3, 0, 13, 13, 14, 13, 2, 14, 14, 13, 14, 13, 14, 0, 0, 13, 13, 0, 0, 13, 14, 0, 3, 14, 12, 0, 10, 13, 1, 3, 14, 2, 0, 12, 0, 0, 13, 1, 3, 14, 14, 0, 1, 3, 13], [0, 11, 0, 13, 11, 14, 0, 0, 0, 7, 12, 12, 2, 0, 14, 0, 10, 12, 12, 12, 0, 8, 14, 11, 0, 0, 13, 14, 0, 13, 3, 14, 10, 0, 14, 0, 0, 0, 14, 14, 0, 7, 13, 3, 3, 14, 13, 2], [14, 14, 0, 0, 0, 7, 8, 13, 0, 0, 1, 1, 6, 0, 0, 13, 5, 0, 0, 6, 11, 14, 8, 7, 6, 13, 9, 8, 5, 12, 7, 5, 7, 7, 6, 13, 0, 0, 5, 12, 0, 0, 1, 7, 0, 0, 11, 11], [0, 0, 8, 9, 6, 9, 3, 1, 2, 0, 0, 8, 0, 6, 8, 2, 9, 6, 6, 1, 0, 1, 3, 2, 0, 6, 8, 6, 3, 1, 10, 8, 0, 0, 9, 9, 8, 13, 3, 8, 10, 0, 8, 0, 0, 13, 6, 6], [2, 12, 1, 6, 13, 12, 6, 7, 6, 12, 0, 0, 12, 1, 12, 8, 0, 0, 2, 8, 0, 0, 12, 13, 13, 12, 12, 2, 8, 4, 14, 13, 0, 0, 8, 12, 14, 12, 7, 2, 0, 0, 4, 8, 8, 0, 14, 0], [11, 5, 9, 5, 0, 0, 11, 16, 0, 14, 16, 6, 0, 0, 3, 5, 0, 10, 14, 9, 14, 16, 0, 0, 14, 11, 11, 9, 0, 0, 9, 11, 0, 3, 0, 14, 10, 11, 0, 0, 9, 9, 11, 10, 10, 11, 0, 8], [0, 6, 14, 14, 0, 0, 12, 12, 0, 0, 11, 10, 11, 13, 11, 11, 0, 3, 0, 11, 0, 11, 0, 12, 0, 0, 3, 5, 0, 14, 12, 6, 0, 11, 0, 5, 0, 3, 12, 11, 0, 14, 6, 12, 0, 0, 12, 12], [0, 0, 7, 11, 0, 0, 0, 0, 11, 9, 9, 5, 0, 11, 7, 6, 6, 0, 5, 0, 2, 9, 6, 9, 2, 0, 7, 0, 11, 6, 0, 0, 0, 0, 11, 10, 0, 0, 0, 0, 0, 11, 5, 9, 9, 9, 4, 5]]
# 755
# 559.79  секунд
#  9.0 - приспособленность в секунду
# 6317.42 819.06
# 5498.360000000001

# 2000 3
# [[12, 0, 0, 8, 5, 9, 8, 13, 0, 8, 12, 12, 2, 9, 0, 0, 0, 2, 10, 8, 0, 14, 14, 5, 0, 10, 8, 9, 0, 8, 9, 13, 0, 5, 4, 10, 0, 0, 9, 9, 5, 9, 14, 4, 0, 0, 13, 12], [14, 7, 0, 0, 0, 14, 12, 14, 0, 13, 5, 10, 0, 0, 7, 7, 0, 14, 5, 14, 7, 3, 12, 9, 7, 8, 7, 7, 0, 0, 13, 5, 7, 13, 13, 14, 0, 0, 14, 14, 10, 10, 0, 0, 0, 3, 8, 13], [0, 14, 1, 10, 14, 4, 13, 9, 0, 14, 13, 4, 0, 12, 5, 5, 0, 13, 13, 9, 0, 0, 8, 8, 0, 0, 13, 12, 14, 14, 14, 4, 8, 9, 0, 0, 0, 0, 4, 5, 14, 5, 4, 12, 14, 14, 14, 14], [0, 0, 14, 3, 0, 11, 14, 11, 0, 0, 9, 14, 0, 13, 9, 9, 3, 9, 8, 6, 14, 13, 13, 14, 14, 3, 0, 14, 0, 0, 3, 3, 1, 8, 0, 0, 11, 8, 8, 8, 0, 13, 13, 6, 1, 9, 10, 4], [0, 0, 7, 6, 6, 8, 5, 6, 1, 3, 2, 8, 13, 7, 8, 8, 6, 0, 6, 0, 0, 0, 3, 6, 0, 7, 3, 8, 0, 0, 6, 14, 0, 6, 2, 5, 14, 6, 3, 13, 0, 1, 1, 13, 0, 13, 6, 2], [5, 13, 4, 12, 0, 6, 7, 12, 7, 7, 0, 5, 0, 0, 12, 1, 0, 5, 1, 13, 8, 0, 0, 1, 0, 0, 5, 4, 7, 1, 12, 7, 0, 14, 14, 0, 7, 14, 6, 6, 0, 0, 5, 14, 6, 6, 12, 5], [0, 16, 11, 14, 13, 5, 2, 16, 0, 12, 11, 3, 14, 0, 14, 0, 14, 10, 14, 12, 0, 0, 5, 12, 2, 14, 14, 5, 0, 0, 5, 11, 11, 16, 10, 2, 0, 2, 12, 11, 0, 14, 10, 5, 0, 0, 3, 10], [6, 5, 12, 5, 3, 2, 0, 0, 10, 5, 7, 13, 0, 11, 11, 11, 0, 6, 9, 2, 11, 0, 7, 0, 0, 9, 11, 2, 3, 10, 10, 12, 14, 10, 12, 7, 2, 13, 13, 2, 0, 6, 7, 11, 0, 0, 0, 0], [4, 10, 9, 13, 0, 0, 11, 2, 14, 11, 4, 6, 0, 5, 2, 14, 0, 0, 12, 4, 0, 6, 10, 11, 13, 4, 12, 11, 10, 6, 0, 0, 0, 2, 6, 13, 0, 10, 10, 4, 4, 12, 12, 2, 0, 0, 5, 6]]
# 375
# 508.83  секунд
#  11.0 - приспособленность в секунду
# 6347.94 539.64
# 5808.299999999999

# 2000 3
# [[5, 8, 0, 0, 0, 0, 8, 5, 8, 10, 12, 8, 0, 0, 7, 13, 9, 8, 14, 9, 13, 2, 12, 4, 0, 0, 4, 9, 0, 5, 5, 7, 14, 3, 8, 11, 12, 13, 10, 13, 0, 12, 12, 4, 0, 0, 2, 14], [13, 14, 10, 13, 0, 0, 14, 12, 13, 14, 10, 7, 2, 14, 8, 14, 0, 0, 1, 1, 1, 14, 0, 0, 0, 10, 1, 1, 8, 12, 14, 5, 0, 14, 4, 3, 0, 2, 7, 3, 0, 0, 2, 14, 0, 13, 5, 12], [0, 12, 7, 4, 11, 7, 4, 9, 0, 0, 4, 2, 9, 12, 14, 5, 0, 5, 4, 5, 0, 0, 2, 11, 14, 4, 12, 0, 0, 14, 11, 8, 0, 4, 12, 9, 0, 0, 14, 4, 14, 14, 5, 5, 0, 5, 8, 2], [0, 13, 8, 14, 1, 13, 1, 13, 0, 0, 0, 0, 0, 0, 3, 2, 13, 2, 6, 7, 0, 6, 6, 14, 3, 2, 8, 14, 3, 0, 0, 3, 0, 0, 14, 4, 6, 14, 8, 6, 3, 0, 0, 2, 1, 9, 9, 7], [6, 0, 0, 9, 0, 0, 9, 2, 2, 2, 9, 9, 11, 0, 0, 6, 11, 14, 0, 0, 0, 9, 9, 6, 8, 8, 0, 0, 0, 3, 3, 11, 9, 6, 3, 6, 13, 0, 0, 14, 0, 0, 8, 3, 0, 6, 11, 9], [8, 2, 12, 6, 14, 5, 0, 14, 0, 0, 14, 10, 0, 5, 5, 12, 5, 0, 5, 0, 0, 0, 5, 13, 10, 7, 7, 5, 0, 7, 7, 12, 2, 10, 6, 12, 2, 0, 1, 0, 0, 1, 13, 6, 0, 0, 12, 5], [10, 5, 14, 2, 0, 11, 5, 16, 0, 0, 0, 0, 14, 3, 16, 9, 14, 9, 9, 14, 0, 0, 14, 8, 0, 0, 14, 10, 0, 9, 9, 9, 5, 5, 0, 0, 0, 11, 13, 9, 11, 6, 11, 10, 14, 3, 14, 11], [0, 9, 3, 11, 5, 2, 11, 10, 6, 0, 7, 14, 0, 0, 11, 11, 3, 6, 10, 11, 0, 0, 10, 2, 0, 14, 10, 12, 12, 13, 13, 14, 6, 0, 0, 5, 11, 7, 9, 11, 5, 0, 0, 13, 5, 4, 0, 0], [2, 11, 0, 0, 0, 8, 6, 7, 10, 7, 2, 13, 0, 11, 12, 4, 0, 10, 13, 4, 11, 11, 13, 5, 0, 0, 13, 4, 11, 11, 4, 4, 11, 0, 11, 0, 0, 0, 4, 2, 7, 10, 7, 0, 10, 11, 6, 13]]
# 685
# 508.85  секунд
#  10.0 - приспособленность в секунду
# 6328.64 809.31
# 5519.33

# 2000 3
# [[1, 4, 5, 4, 8, 12, 5, 8, 0, 12, 10, 13, 5, 9, 0, 0, 0, 4, 12, 12, 0, 0, 13, 11, 0, 0, 13, 10, 0, 8, 13, 8, 0, 9, 8, 9, 2, 8, 0, 0, 8, 11, 11, 2, 8, 4, 8, 9], [14, 13, 8, 12, 3, 2, 0, 0, 0, 7, 7, 0, 6, 6, 14, 12, 5, 13, 0, 0, 14, 2, 8, 8, 0, 4, 3, 0, 10, 13, 0, 2, 0, 0, 12, 14, 0, 2, 13, 8, 10, 14, 14, 10, 14, 3, 10, 10], [12, 11, 9, 14, 11, 9, 13, 7, 14, 4, 12, 3, 14, 4, 0, 14, 11, 0, 0, 7, 0, 0, 12, 13, 7, 12, 9, 5, 0, 12, 4, 5, 11, 14, 11, 2, 0, 14, 11, 4, 2, 13, 0, 0, 0, 0, 13, 13], [6, 8, 14, 11, 0, 0, 3, 5, 8, 8, 14, 14, 0, 5, 3, 8, 0, 0, 14, 11, 0, 14, 14, 9, 1, 1, 11, 3, 9, 14, 2, 14, 14, 13, 13, 13, 0, 0, 2, 13, 0, 0, 0, 0, 6, 14, 14, 6], [0, 5, 2, 7, 0, 13, 8, 3, 0, 11, 1, 6, 0, 0, 6, 7, 12, 9, 2, 8, 6, 11, 1, 7, 0, 8, 6, 4, 0, 6, 14, 13, 2, 3, 3, 5, 0, 11, 6, 6, 14, 0, 9, 0, 1, 13, 3, 8], [0, 6, 6, 5, 12, 14, 14, 12, 0, 14, 4, 12, 0, 12, 12, 1, 0, 5, 7, 1, 0, 0, 7, 14, 14, 7, 12, 7, 0, 0, 12, 12, 0, 5, 6, 4, 12, 12, 12, 1, 0, 5, 6, 12, 0, 0, 12, 12], [0, 14, 11, 9, 5, 0, 2, 0, 11, 2, 5, 11, 2, 2, 5, 5, 0, 14, 11, 16, 0, 0, 5, 16, 0, 0, 16, 14, 3, 0, 0, 10, 0, 0, 16, 10, 14, 5, 14, 11, 0, 3, 3, 14, 0, 0, 5, 3], [10, 2, 12, 13, 0, 6, 10, 11, 3, 0, 0, 9, 0, 0, 11, 10, 2, 11, 4, 5, 3, 7, 0, 5, 0, 9, 5, 13, 0, 11, 6, 7, 0, 7, 5, 12, 11, 9, 0, 0, 0, 7, 0, 7, 0, 7, 7, 14], [0, 0, 13, 2, 6, 11, 7, 4, 0, 0, 8, 1, 0, 11, 13, 9, 0, 0, 13, 14, 0, 0, 11, 2, 0, 11, 14, 12, 5, 2, 11, 0, 7, 0, 0, 6, 0, 7, 9, 5, 6, 4, 5, 4, 11, 5, 0, 0]]
# 610
# 505.69  секунд
#  11.0 - приспособленность в секунду
# 6362.92 749.27
# 5613.65

# 2000 2.5
# [[7, 2, 0, 0, 12, 8, 9, 10, 0, 7, 5, 10, 9, 8, 8, 9, 0, 8, 13, 13, 9, 0, 0, 9, 7, 13, 5, 8, 0, 8, 13, 8, 4, 2, 2, 4, 9, 0, 8, 0, 0, 12, 8, 13, 8, 0, 8, 0], [12, 13, 0, 0, 10, 14, 6, 0, 0, 0, 12, 13, 0, 0, 12, 7, 1, 0, 0, 2, 0, 7, 6, 13, 0, 0, 14, 10, 13, 10, 6, 1, 12, 13, 6, 2, 10, 0, 0, 14, 0, 0, 14, 10, 10, 2, 1, 14], [0, 0, 14, 14, 0, 0, 5, 12, 0, 12, 13, 12, 14, 11, 7, 13, 8, 5, 9, 9, 4, 11, 14, 14, 0, 8, 13, 13, 0, 0, 5, 13, 0, 0, 9, 5, 0, 12, 12, 7, 13, 11, 9, 8, 7, 4, 5, 9], [14, 9, 9, 3, 0, 11, 11, 13, 0, 0, 3, 9, 0, 0, 2, 14, 0, 3, 2, 8, 14, 1, 1, 11, 14, 14, 2, 14, 0, 14, 8, 5, 1, 8, 0, 8, 14, 6, 14, 9, 9, 8, 0, 0, 0, 0, 6, 5], [0, 0, 11, 11, 0, 2, 8, 2, 0, 9, 6, 7, 0, 0, 9, 8, 0, 0, 0, 0, 3, 9, 9, 6, 1, 1, 6, 7, 9, 6, 0, 0, 11, 0, 8, 0, 6, 2, 7, 8, 0, 3, 7, 9, 1, 6, 0, 3], [1, 12, 12, 5, 13, 7, 1, 14, 1, 2, 0, 5, 0, 0, 0, 0, 13, 14, 5, 12, 0, 5, 13, 2, 0, 0, 12, 2, 0, 5, 1, 12, 0, 14, 14, 12, 0, 14, 5, 12, 12, 7, 2, 1, 0, 5, 14, 13], [0, 0, 0, 0, 2, 12, 14, 9, 0, 5, 14, 14, 3, 2, 5, 12, 12, 12, 14, 5, 10, 14, 11, 12, 11, 11, 10, 0, 11, 3, 0, 0, 0, 10, 12, 9, 0, 11, 9, 5, 5, 14, 5, 5, 0, 14, 12, 8], [10, 6, 7, 9, 6, 5, 12, 5, 0, 0, 10, 2, 0, 6, 0, 3, 11, 7, 7, 7, 0, 12, 12, 0, 9, 6, 9, 12, 0, 12, 12, 7, 6, 0, 0, 11, 3, 5, 10, 2, 2, 0, 12, 0, 0, 10, 9, 7], [0, 11, 2, 7, 0, 0, 13, 7, 11, 11, 9, 4, 11, 4, 11, 11, 0, 10, 10, 10, 0, 0, 4, 5, 0, 5, 4, 5, 0, 9, 11, 11, 0, 7, 11, 7, 4, 13, 2, 4, 0, 5, 10, 7, 0, 0, 11, 11]]
# 600
# 455.32  секунд
#  12.0 - приспособленность в секунду
# 6356.42 682.66
# 5673.76

# 2000 2.5
# [[0, 0, 9, 5, 8, 12, 14, 4, 4, 0, 8, 0, 0, 10, 8, 9, 10, 9, 5, 10, 0, 8, 5, 10, 9, 14, 5, 8, 5, 4, 14, 2, 0, 0, 4, 14, 4, 13, 8, 3, 0, 0, 2, 9, 0, 0, 12, 8], [3, 3, 1, 13, 0, 8, 12, 6, 1, 0, 0, 14, 0, 14, 12, 14, 14, 8, 0, 0, 12, 0, 0, 7, 2, 0, 2, 0, 0, 8, 13, 8, 0, 0, 14, 2, 3, 8, 14, 14, 0, 0, 6, 11, 0, 2, 14, 6], [0, 0, 4, 4, 2, 11, 0, 0, 0, 0, 0, 0, 14, 5, 14, 4, 4, 13, 13, 13, 13, 11, 11, 4, 0, 11, 4, 13, 0, 14, 5, 13, 11, 10, 0, 0, 14, 5, 4, 4, 0, 14, 14, 14, 0, 5, 5, 4], [0, 9, 14, 14, 6, 6, 3, 3, 0, 14, 5, 3, 0, 8, 3, 5, 0, 0, 9, 14, 0, 14, 8, 8, 0, 5, 14, 3, 0, 0, 12, 14, 8, 3, 9, 5, 11, 14, 11, 9, 1, 6, 0, 0, 11, 8, 0, 0], [5, 6, 8, 7, 0, 0, 7, 8, 0, 5, 6, 11, 0, 2, 7, 8, 3, 5, 7, 8, 3, 5, 0, 0, 0, 3, 9, 11, 2, 12, 2, 7, 5, 8, 8, 7, 0, 4, 5, 11, 0, 0, 5, 8, 0, 0, 6, 11], [0, 12, 5, 2, 4, 0, 0, 14, 0, 12, 4, 7, 12, 12, 13, 13, 0, 4, 14, 4, 0, 4, 4, 12, 0, 0, 6, 14, 13, 3, 7, 5, 14, 12, 12, 12, 0, 0, 0, 0, 14, 4, 8, 12, 14, 7, 2, 2], [0, 14, 11, 0, 14, 14, 5, 0, 0, 11, 11, 12, 0, 0, 5, 2, 0, 11, 11, 2, 11, 0, 2, 2, 16, 0, 0, 12, 14, 0, 11, 0, 0, 14, 2, 0, 0, 2, 2, 5, 5, 5, 0, 16, 0, 0, 13, 5], [11, 0, 0, 11, 0, 0, 11, 11, 12, 6, 3, 0, 3, 0, 11, 0, 0, 2, 2, 6, 0, 3, 7, 0, 10, 7, 10, 7, 0, 6, 0, 11, 2, 13, 0, 0, 0, 11, 6, 13, 0, 2, 12, 2, 0, 0, 10, 12], [0, 5, 7, 9, 11, 4, 4, 9, 0, 0, 14, 4, 0, 4, 4, 7, 7, 0, 4, 0, 14, 7, 14, 14, 0, 4, 0, 9, 0, 11, 9, 4, 0, 7, 11, 10, 5, 0, 0, 12, 11, 11, 11, 7, 2, 10, 4, 14]]
# 735
# 470.55  секунд
#  11.0 - приспособленность в секунду
# 6374.74 849.62
# 5525.12

# 2000 2
# [[0, 13, 9, 4, 0, 0, 8, 13, 0, 8, 4, 4, 9, 13, 13, 8, 0, 0, 13, 8, 8, 8, 4, 8, 9, 10, 10, 13, 8, 8, 9, 4, 0, 14, 4, 13, 0, 0, 8, 8, 8, 9, 0, 8, 0, 0, 4, 10], [0, 0, 7, 8, 0, 0, 14, 14, 0, 0, 10, 10, 0, 5, 8, 13, 14, 13, 8, 5, 14, 4, 13, 13, 0, 0, 3, 14, 0, 13, 14, 2, 14, 4, 14, 3, 14, 8, 13, 5, 0, 14, 7, 14, 7, 0, 0, 2], [0, 0, 11, 5, 14, 13, 0, 0, 0, 5, 14, 2, 14, 8, 11, 12, 0, 8, 14, 12, 0, 5, 5, 11, 8, 13, 12, 8, 0, 14, 5, 14, 0, 0, 13, 12, 2, 14, 5, 13, 0, 0, 13, 12, 5, 8, 8, 0], [0, 14, 13, 14, 0, 1, 6, 3, 0, 1, 13, 13, 0, 0, 1, 14, 6, 3, 6, 14, 0, 14, 3, 2, 14, 6, 0, 0, 0, 1, 2, 0, 0, 13, 6, 0, 0, 0, 1, 2, 0, 0, 8, 13, 0, 0, 13, 8], [0, 9, 0, 3, 13, 6, 1, 6, 0, 13, 2, 8, 0, 3, 6, 1, 0, 0, 2, 11, 13, 0, 6, 0, 0, 1, 13, 6, 0, 0, 6, 6, 3, 3, 9, 6, 0, 11, 11, 0, 6, 13, 2, 6, 1, 0, 0, 6], [12, 5, 1, 6, 8, 14, 12, 12, 1, 0, 7, 0, 1, 6, 14, 7, 0, 0, 12, 1, 1, 12, 0, 0, 0, 0, 8, 5, 1, 12, 12, 12, 0, 12, 8, 8, 0, 0, 7, 12, 0, 0, 14, 5, 14, 6, 12, 5], [0, 11, 14, 11, 0, 5, 11, 11, 14, 14, 0, 0, 5, 14, 0, 0, 2, 0, 9, 0, 7, 2, 0, 0, 7, 14, 7, 2, 14, 11, 0, 11, 0, 5, 11, 14, 0, 0, 14, 14, 0, 0, 0, 0, 0, 0, 14, 14], [11, 6, 5, 12, 0, 0, 0, 0, 11, 0, 0, 7, 0, 0, 12, 11, 11, 7, 0, 0, 5, 0, 11, 0, 3, 12, 5, 11, 12, 0, 11, 0, 6, 8, 3, 5, 0, 0, 12, 7, 3, 3, 11, 11, 11, 3, 0, 0], [5, 4, 0, 0, 0, 11, 13, 9, 4, 9, 9, 14, 0, 12, 5, 9, 0, 11, 4, 7, 0, 13, 14, 5, 11, 4, 4, 12, 0, 0, 13, 5, 11, 11, 5, 11, 0, 0, 9, 11, 0, 7, 9, 9, 9, 11, 11, 13]]
# 715
# 424.54  секунд
#  12.0 - приспособленность в секунду
# 6356.54 884.98
# 5471.5599999999995

# 2000 2
# [[9, 9, 14, 8, 13, 12, 14, 14, 0, 0, 0, 0, 0, 2, 9, 12, 9, 12, 2, 9, 0, 12, 12, 9, 0, 13, 14, 13, 0, 13, 13, 2, 13, 13, 2, 1, 0, 12, 9, 9, 0, 12, 6, 9, 0, 0, 9, 2], [14, 1, 8, 12, 7, 3, 0, 0, 14, 13, 13, 13, 0, 0, 8, 14, 0, 0, 12, 7, 14, 14, 14, 7, 8, 3, 7, 14, 3, 3, 6, 7, 0, 0, 7, 7, 14, 3, 3, 8, 11, 6, 0, 0, 14, 8, 0, 0], [0, 14, 13, 13, 0, 0, 12, 12, 0, 12, 12, 12, 0, 9, 14, 13, 14, 14, 13, 5, 13, 5, 9, 0, 0, 9, 9, 9, 0, 9, 9, 9, 0, 9, 9, 9, 0, 0, 14, 7, 0, 9, 5, 14, 9, 14, 12, 9], [0, 7, 6, 6, 0, 0, 13, 13, 0, 2, 8, 14, 0, 0, 11, 6, 11, 6, 6, 14, 6, 8, 7, 14, 11, 14, 8, 8, 0, 0, 14, 8, 0, 6, 8, 14, 8, 14, 7, 0, 0, 0, 4, 3, 0, 2, 8, 14], [0, 0, 11, 11, 9, 7, 7, 7, 6, 6, 14, 11, 6, 5, 0, 0, 0, 0, 0, 0, 11, 9, 11, 0, 6, 7, 11, 6, 5, 7, 11, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 6, 11, 11, 6, 0], [0, 12, 12, 5, 12, 4, 0, 0, 0, 0, 6, 6, 0, 4, 5, 5, 0, 0, 5, 12, 12, 4, 4, 12, 12, 12, 12, 4, 12, 0, 8, 0, 0, 0, 12, 12, 0, 0, 13, 12, 0, 0, 12, 10, 8, 4, 2, 4], [3, 16, 9, 14, 0, 0, 11, 11, 0, 0, 11, 3, 0, 0, 12, 11, 0, 3, 14, 11, 0, 3, 0, 11, 14, 16, 0, 0, 0, 14, 16, 14, 0, 0, 14, 16, 0, 0, 5, 11, 0, 14, 9, 12, 0, 0, 16, 12], [5, 0, 1, 0, 3, 11, 2, 3, 13, 11, 2, 5, 3, 0, 2, 0, 2, 0, 0, 2, 3, 13, 2, 13, 0, 0, 3, 3, 7, 0, 0, 13, 7, 3, 0, 0, 0, 0, 4, 14, 7, 11, 0, 0, 0, 0, 14, 7], [4, 8, 4, 2, 14, 13, 0, 0, 0, 0, 0, 0, 4, 11, 4, 2, 4, 4, 4, 4, 4, 6, 13, 2, 4, 11, 4, 11, 0, 11, 2, 12, 0, 0, 11, 11, 0, 4, 11, 2, 0, 2, 2, 5, 0, 6, 11, 11]]
# 760
# 415.14  секунд
#  13.0 - приспособленность в секунду
# 6326.32 830.34
# 5495.98

# 2000 3 + новое скрещивание
# [[0, 2, 9, 8, 0, 1, 4, 5, 0, 8, 3, 5, 0, 8, 8, 12, 0, 10, 4, 12, 0, 2, 11, 7, 0, 5, 13, 7, 2, 0, 0, 13, 0, 0, 4, 9, 12, 14, 9, 10, 10, 6, 14, 11, 0, 8, 8, 13], [1, 12, 11, 12, 0, 0, 13, 3, 0, 0, 8, 4, 14, 6, 7, 14, 7, 1, 13, 14, 10, 0, 0, 2, 0, 8, 14, 1, 0, 0, 6, 10, 12, 3, 5, 2, 0, 10, 14, 3, 2, 9, 7, 5, 0, 0, 13, 14], [0, 0, 13, 13, 14, 12, 12, 14, 0, 0, 12, 2, 10, 3, 9, 2, 5, 13, 8, 4, 0, 0, 14, 9, 4, 14, 11, 8, 6, 14, 9, 10, 14, 4, 0, 0, 0, 0, 1, 7, 0, 5, 11, 2, 0, 5, 7, 11], [0, 14, 5, 9, 3, 13, 14, 11, 0, 3, 7, 3, 2, 0, 0, 10, 12, 6, 7, 6, 13, 14, 0, 0, 0, 11, 8, 13, 9, 5, 14, 1, 0, 0, 14, 8, 1, 2, 8, 2, 0, 0, 4, 6, 0, 11, 14, 1], [7, 5, 6, 2, 0, 0, 0, 0, 3, 7, 9, 8, 6, 13, 0, 0, 1, 14, 12, 8, 2, 6, 13, 1, 0, 0, 9, 14, 10, 6, 3, 4, 6, 5, 0, 0, 0, 7, 11, 8, 0, 11, 2, 13, 11, 3, 1, 6], [12, 7, 14, 6, 7, 6, 1, 12, 0, 4, 5, 13, 0, 9, 3, 8, 0, 0, 5, 2, 0, 0, 8, 12, 0, 13, 7, 2, 0, 0, 4, 14, 0, 6, 1, 11, 10, 12, 5, 10, 14, 12, 0, 0, 2, 12, 10, 1], [14, 10, 2, 11, 11, 2, 5, 13, 0, 0, 11, 11, 12, 14, 2, 16, 0, 0, 11, 11, 0, 0, 3, 4, 6, 15, 10, 0, 0, 3, 5, 5, 1, 8, 10, 14, 0, 9, 7, 16, 0, 14, 9, 14, 0, 0, 12, 3], [5, 0, 0, 14, 0, 9, 10, 2, 11, 5, 14, 6, 0, 5, 10, 7, 11, 0, 1, 0, 4, 11, 9, 13, 10, 2, 3, 12, 0, 2, 13, 3, 11, 11, 6, 7, 0, 0, 11, 12, 0, 3, 12, 8, 7, 6, 0, 0], [11, 0, 8, 0, 2, 10, 7, 7, 13, 11, 2, 9, 5, 11, 0, 0, 14, 5, 0, 0, 12, 4, 6, 11, 2, 6, 5, 11, 0, 10, 10, 6, 0, 0, 3, 4, 4, 11, 0, 0, 7, 13, 13, 1, 0, 14, 9, 12]]
# 1375
# 489.57  секунд
#  10.0 - приспособленность в секунду
# 6351.7 1377.72
# 4973.98