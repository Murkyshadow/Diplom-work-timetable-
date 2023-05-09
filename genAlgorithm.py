import sqlite3
import time
from copy import deepcopy
from PyQt5.QtWidgets import QLineEdit
import PyQt5
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
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

class GeneticGenerationTimeTable():
    def __init__(self, group_lesson, AllTeacherTimeWork, lessonID_teacherID, parLesson_group):
        """запросы к бд + 1 поколение"""
        # QLineEdit.
        # self.DB = DB
        self.group_lesson, self.index_lesson, self.index_group = group_lesson  # id_lesson - по индексу обращаемся к уроку
        self.teacherID_TimeWork = AllTeacherTimeWork  # {teacherID:[{day:{numLesson:True|False}}, day:{numLesson:True|False}}]} - 2 недели
        self.parLesson_group = parLesson_group
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
        self.lesson_teacherID = lessonID_teacherID
        # print(self.lesson_teacherID)
        # print(self.group_lesson, self.index_lesson, self.teacherID_TimeWork, self.lesson_teacherID, sep='\n')


    def random_timeTable(self):
        """первое поколение"""
        TimeTable = deepcopy(self.group_lesson)
        for num_group in range(len(TimeTable)):
            random.shuffle(TimeTable[num_group])
        individ = Individual(TimeTable, self.TimeTable_Fitness(TimeTable), info = 'Первое поколение')
        # return creator.Individual(TimeTable)
        return individ

    def TimeTable_Fitness(self, individual):
        parLesson = self.parLesson_group
        fitness = 0
        teacherID_TimeWork = deepcopy(self.teacherID_TimeWork)
        for num_group in range(len(individual)):
            for week in range(0, 2):
                count_lesson_week = 0
                for day in range(0, 6):
                    windowsGroup = False
                    count_lesson_day = 0
                    for num_lesson in range(week*6*4 + day*4, week*6*4 + day*4 + 4):
                        lesson = self.index_lesson[num_group][individual[num_group][num_lesson]]
                        if lesson != None:
                            if windowsGroup:    # после (окна свободное время) значит это окно
                                windowsGroup = 2
                            count_lesson_day += 1    # кол-во пар в день
                            if not teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][num_lesson%4]:    # если у учителя нет этой пары (методичсеский дни)
                                fitness += 10
                                # print('методическое расписание учителя')
                            elif teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][num_lesson%4] == True:  # отмечаем, что пара
                                teacherID_TimeWork[self.lesson_teacherID[lesson]][week][day][num_lesson%4] = -1
                            # elif lesson in parLesson.keys():   # спаренная пара
                            #     parLesson[lesson][self.index_group[num_group]].append(num_lesson)
                            elif lesson not in parLesson:   # уже есть пара у учителя
                                fitness += 50
                                # print('уже есть пара')
                            if week == 1 and self.index_lesson[num_group][individual[num_group][num_lesson]] != self.index_lesson[num_group][individual[num_group][num_lesson-24]]:
                                fitness += 0.001
                            try:    # для спаренных пар
                                parLesson[lesson][self.index_group[num_group]].append(num_lesson)
                            except KeyError:
                                pass

                        elif count_lesson_day >= 1 and windowsGroup == False:     # нет пары (окно)
                            windowsGroup = True
                    if windowsGroup == 2:
                        fitness += 20
                        # print('окно у группы', self.index_group[num_group], day)
                    if count_lesson_day <= 1:
                        fitness += 50 * (count_lesson_day+1)
                        # print('мало пар')
                    count_lesson_week += count_lesson_day
                fitness += 5 * abs(18-count_lesson_week) # должно быть 18 пар в неделю

        # проверяем разницу для спаренных пар
        for lessonID in parLesson:
            groups = list(parLesson[lessonID].keys())
            for i in range(1, len(parLesson[lessonID])):
                fitness += len(set(parLesson[lessonID][groups[i]]) - set(parLesson[lessonID][groups[i-1]])) * 20

        for id in teacherID_TimeWork:
            for week in range(2):
                for day in range(6):
                    count_lesson_day = 0
                    windowsTeacher = False
                    for num_lesson in teacherID_TimeWork[id][week][day]:
                        lesson = teacherID_TimeWork[id][week][day][num_lesson]
                        if lesson == -1:    # есть пара
                            count_lesson_day += 1
                            if windowsTeacher:  # после окна пара
                                windowsTeacher = 2

                        elif lesson == True and count_lesson_day >= 1 and windowsTeacher == False:     # нет пары (окно)
                            windowsTeacher = True
                    if windowsTeacher == 2: # без окон
                        fitness += 5
                    if count_lesson_day == 1:   # минимум 2 пары в день
                        fitness += 10

        return fitness

    def cxOrder(self, ind1, ind2):
        ind1 = deepcopy(ind1)
        ind2 = deepcopy(ind2)
        size = len(ind1)
        a, b = random.sample(range(size), 2)
        a, b = min([a, b]), max([a, b])
        while a==0 and b==size:
            a, b = random.sample(range(size), 2)
            a, b = min([a, b]), max([a, b])

        for num_group in range(a, b):
            ind1[num_group], ind2[num_group] = ind2[num_group], ind1[num_group]
        return ind1, ind2

    def mutationTimeTable(self, individual):
        individual = deepcopy(individual)
        for numGroup in range(len(individual)):
        # for _ in range(random.randint(1, 1)):
        #     numGroup = random.randint(0, len(individual)-1)
            if random.random() < 0.3:  # вероятность в группе
                for i in range(len(individual[numGroup])):
                    # tools.mutShuffleIndexes(individual, indpb)
                    if random.random() < 0.015:  # сила мутации в расписании групппы
                        # type_mutation = random.sample([2], 1)
                        # num_day = i // 4
                        # if type_mutation == 0:  # меняем дни местами
                        #     random_day = random.randint(0, 47//4)
                        #     for shift_lesson in range(0,4):
                        #         individual[numGroup][num_day*4+shift_lesson], individual[numGroup][random_day*4+shift_lesson] = individual[numGroup][random_day*4+shift_lesson], individual[numGroup][num_day*4+shift_lesson]
                        # # elif type_mutation == 1:    # перемешиваем пары за день
                        # #     day_lesson = individual[numGroup][num_day*4:(num_day+1)*4]
                        # #     random.shuffle(day_lesson)
                        # #     individual[numGroup][num_day * 4:(num_day+1)*4] = day_lesson
                        # else:   # меняем 2 пары местами
                        random_gen = random.randint(0, len(individual[numGroup])-1)
                        while individual[numGroup][i] == individual[numGroup][random_gen]:
                            random_gen = random.randint(0, len(individual[numGroup]) - 1)
                        individual[numGroup][i], individual[numGroup][random_gen] = individual[numGroup][random_gen], individual[numGroup][i]

                        # for _ in range(random.randint(1,3)):
                        #     random_gen = random.randint(0, len(individual[numGroup])-1)
                        #     random_gen_2 = random.randint(0, len(individual[numGroup])-1)
                        #     individual[numGroup][random_gen_2], individual[numGroup][random_gen] = individual[numGroup][random_gen], individual[numGroup][random_gen_2]

        return individual

    def get_TimeTable_for_save(self, TimeTable):
        TimeTable_for_save = []
        for num_group, group in enumerate(TimeTable):
            TimeTable_for_save.append([])
            for ind_lesson in group:
                TimeTable_for_save[-1].append(self.index_lesson[num_group][ind_lesson])
        return TimeTable_for_save

    def tournament_selection(self, population, k, num_parents):
        # population - список особей
        # k - количество участников в турнире
        # num_parents - количество родительских особей, которые нужно выбрать

        # создаем пул доступных особей
        available_parents = list(range(len(population)))
        selected_parents = []
        for i in range(num_parents):
            # выбираем k участников для турнира и находим лучшую особь по заданному критерию
            best = min(random.sample(available_parents, k), key=lambda x: population[x].fitness)
            # добавляем лучшую особь в список отобранных родительских особей
            selected_parents.append(population[best])
            # удаляем особь из пула доступных особей
            available_parents.remove(best)
            # если пул доступных особей пуст, перезаполняем его
            # if not available_parents:
            #     available_parents = list(range(len(population)))

        return selected_parents + self.best_individs

    def save_best_individ(self, population, k):
        from math import inf
        if k <= 0:
            index_min = min(range(len(population)), key=lambda i: population[i].fitness)
            min_individ = population[index_min]
            return min_individ.fitness, min_individ.info

        self.best_individs = sorted(population[:k], key=lambda ind: ind.fitness)
        # best_fitness = inf
        # for _ in range(k):
        #     index_min = min(range(len(population)), key=lambda i: population[i].fitness)
        #     min_individ = population[index_min]
        #     self.best_individs.append(min_individ)
        #     # if min_individ.fitness < best_fitness:
        #     #     best_fitness = min_individ.fitness
        #     population.pop(index_min)
        for individ in population[k:]:
            if individ.fitness < self.best_individs[-1].fitness:
                self.best_individs[-1] = individ
                i = k-2
                while i != 0 and self.best_individs[i+1].fitness < self.best_individs[i].fitness:
                    self.best_individs[i + 1].fitness, self.best_individs[i].fitness = self.best_individs[i].fitness, self.best_individs[i+1].fitness

        index_min = min(range(len(self.best_individs)), key=lambda i: self.best_individs[i].fitness)
        return self.best_individs[index_min].fitness, self.best_individs[index_min].info

class Individual():
    def __init__(self, data, fitness, info):
        self.timeTable = data
        self.fitness = fitness
        self.info = info

class GA(QThread):
    result = pyqtSignal(list)
    progress = pyqtSignal(int)
    def __init__(self,  group_lesson, AllTeacherTimeWork, lessonID_teacherID, parLesson_group):
        super(GA, self).__init__()
        self.group_lesson, self.AllTeacherTimeWork, self.lessonID_teacherID, self.parLesson_group =  group_lesson, AllTeacherTimeWork, lessonID_teacherID, parLesson_group
        # generation = GeneticGenerationTimeTable(DB)
        # print(generation.TimeTable_Fitness([[34, 47, 27, 24, 31, 6, 1, 21, 38, 39, 40, 30, 7, 8, 22, 46, 18, 36, 33, 12, 4, 2, 20, 26, 10, 29, 35, 14, 0, 32, 41, 37, 5, 23, 28, 25, 11, 45, 16, 43, 15, 44, 13, 19, 3, 17, 42, 9], [18, 28, 30, 6, 35, 16, 42, 38, 0, 7, 33, 40, 19, 47, 44, 4, 11, 34, 21, 32, 36, 12, 27, 8, 1, 31, 22, 13, 23, 43, 26, 14, 29, 17, 9, 10, 2, 46, 24, 37, 15, 20, 41, 5, 39, 25, 45, 3], [26, 21, 18, 43, 23, 39, 17, 13, 3, 40, 38, 34, 32, 7, 24, 2, 27, 1, 22, 6, 31, 29, 15, 9, 0, 19, 14, 28, 12, 45, 41, 35, 8, 44, 33, 47, 46, 20, 5, 11, 36, 4, 10, 37, 30, 16, 25, 42], [25, 34, 2, 5, 6, 30, 44, 12, 29, 22, 17, 3, 42, 7, 40, 1, 43, 20, 16, 33, 47, 41, 39, 21, 4, 27, 26, 10, 36, 18, 32, 38, 46, 24, 19, 8, 9, 23, 15, 31, 14, 28, 37, 35, 11, 0, 45, 13], [39, 22, 31, 2, 46, 47, 13, 6, 4, 10, 33, 40, 25, 34, 32, 3, 1, 17, 36, 24, 44, 38, 37, 18, 23, 5, 15, 8, 27, 26, 21, 12, 20, 28, 45, 43, 11, 7, 42, 29, 0, 9, 35, 30, 14, 41, 19, 16], [40, 30, 4, 1, 45, 21, 17, 26, 43, 39, 19, 28, 32, 34, 3, 8, 22, 18, 33, 42, 20, 9, 11, 24, 6, 10, 15, 38, 16, 31, 44, 41, 0, 36, 46, 7, 27, 12, 14, 23, 25, 35, 47, 29, 13, 37, 5, 2], [17, 28, 22, 16, 20, 47, 41, 9, 36, 26, 34, 3, 21, 0, 18, 4, 25, 27, 35, 19, 2, 11, 14, 12, 1, 42, 39, 44, 15, 10, 31, 6, 38, 5, 40, 8, 37, 43, 30, 24, 32, 45, 46, 33, 7, 23, 13, 29], [7, 21, 16, 36, 45, 27, 41, 10, 12, 19, 47, 33, 15, 28, 25, 26, 35, 14, 9, 8, 24, 29, 11, 6, 17, 18, 39, 31, 42, 23, 13, 37, 2, 44, 46, 38, 30, 4, 43, 0, 3, 34, 22, 32, 40, 5, 20, 1], [5, 13, 27, 44, 32, 39, 12, 40, 33, 15, 18, 42, 34, 21, 2, 11, 0, 35, 17, 4, 36, 16, 30, 1, 38, 28, 19, 8, 3, 22, 14, 9, 10, 41, 25, 45, 20, 6, 26, 7, 29, 23, 43, 31, 46, 37, 47, 24]])[0])
        # generation.save_TimeTable_in_DB([[34, 47, 27, 24, 31, 6, 1, 21, 38, 39, 40, 30, 7, 8, 22, 46, 18, 36, 33, 12, 4, 2, 20, 26, 10, 29, 35, 14, 0, 32, 41, 37, 5, 23, 28, 25, 11, 45, 16, 43, 15, 44, 13, 19, 3, 17, 42, 9], [18, 28, 30, 6, 35, 16, 42, 38, 0, 7, 33, 40, 19, 47, 44, 4, 11, 34, 21, 32, 36, 12, 27, 8, 1, 31, 22, 13, 23, 43, 26, 14, 29, 17, 9, 10, 2, 46, 24, 37, 15, 20, 41, 5, 39, 25, 45, 3], [26, 21, 18, 43, 23, 39, 17, 13, 3, 40, 38, 34, 32, 7, 24, 2, 27, 1, 22, 6, 31, 29, 15, 9, 0, 19, 14, 28, 12, 45, 41, 35, 8, 44, 33, 47, 46, 20, 5, 11, 36, 4, 10, 37, 30, 16, 25, 42], [25, 34, 2, 5, 6, 30, 44, 12, 29, 22, 17, 3, 42, 7, 40, 1, 43, 20, 16, 33, 47, 41, 39, 21, 4, 27, 26, 10, 36, 18, 32, 38, 46, 24, 19, 8, 9, 23, 15, 31, 14, 28, 37, 35, 11, 0, 45, 13], [39, 22, 31, 2, 46, 47, 13, 6, 4, 10, 33, 40, 25, 34, 32, 3, 1, 17, 36, 24, 44, 38, 37, 18, 23, 5, 15, 8, 27, 26, 21, 12, 20, 28, 45, 43, 11, 7, 42, 29, 0, 9, 35, 30, 14, 41, 19, 16], [40, 30, 4, 1, 45, 21, 17, 26, 43, 39, 19, 28, 32, 34, 3, 8, 22, 18, 33, 42, 20, 9, 11, 24, 6, 10, 15, 38, 16, 31, 44, 41, 0, 36, 46, 7, 27, 12, 14, 23, 25, 35, 47, 29, 13, 37, 5, 2], [17, 28, 22, 16, 20, 47, 41, 9, 36, 26, 34, 3, 21, 0, 18, 4, 25, 27, 35, 19, 2, 11, 14, 12, 1, 42, 39, 44, 15, 10, 31, 6, 38, 5, 40, 8, 37, 43, 30, 24, 32, 45, 46, 33, 7, 23, 13, 29], [7, 21, 16, 36, 45, 27, 41, 10, 12, 19, 47, 33, 15, 28, 25, 26, 35, 14, 9, 8, 24, 29, 11, 6, 17, 18, 39, 31, 42, 23, 13, 37, 2, 44, 46, 38, 30, 4, 43, 0, 3, 34, 22, 32, 40, 5, 20, 1], [5, 13, 27, 44, 32, 39, 12, 40, 33, 15, 18, 42, 34, 21, 2, 11, 0, 35, 17, 4, 36, 16, 30, 1, 38, 28, 19, 8, 3, 22, 14, 9, 10, 41, 25, 45, 20, 6, 26, 7, 29, 23, 43, 31, 46, 37, 47, 24]])
        # print(generation.TimeTable_Fitness([[2, 15, 47, 16, 45, 19, 9, 3, 13, 6, 38, 0, 5, 37, 33, 27, 29, 14, 21, 20, 25, 39, 34, 30, 8, 42, 26, 18, 36, 17, 12, 4, 31, 32, 28, 43, 11, 10, 22, 24, 44, 41, 46, 35, 23, 40, 7, 1], [42, 32, 35, 16, 8, 3, 41, 28, 15, 30, 34, 38, 14, 24, 19, 18, 0, 5, 26, 29, 10, 9, 23, 17, 25, 37, 4, 6, 1, 47, 12, 31, 7, 2, 20, 21, 44, 22, 40, 45, 46, 33, 39, 36, 11, 13, 27, 43]]))
        # print(generation.save_TimeTable_in_DB([[18, 27, 26, 42, 4, 38, 13, 6, 1, 34, 24, 5, 32, 43, 41, 44, 22, 16, 0, 8, 31, 37, 23, 28, 9, 11, 46, 17, 29, 36, 47, 30, 21, 15, 33, 7, 3, 25, 45, 39, 20, 19, 40, 14, 10, 2, 12, 35], [32, 33, 46, 2, 1, 13, 31, 37, 24, 23, 36, 30, 0, 29, 20, 26, 44, 5, 43, 3, 28, 27, 45, 4, 15, 34, 12, 9, 39, 22, 10, 8, 35, 42, 19, 21, 6, 47, 18, 7, 11, 41, 14, 40, 17, 25, 38, 16]]))
        # for POPULATION_SIZE in range(50, 131, 20):
        #     print(POPULATION_SIZE)
        #     middle_time = 0
        #     middle_combined_lesson = 0
        #     n = 5
        #     for _ in range(1,1+n):

    def run(self):
        # константы генетического алгоритма
        print('start generate')
        generation = GeneticGenerationTimeTable(self.group_lesson, self.AllTeacherTimeWork, self.lessonID_teacherID, self.parLesson_group)
        POPULATION_SIZE = 60       # количество индивидуумов в популяции
        P_CROSSOVER = 0.4          # вероятность скрещивания
        P_MUTATION = 0.2           # вероятность мутации индивидуума
        # MAX_GENERATIONS = 600       # максимальное количество поколений
        # HALL_OF_FAME_SIZE = 1
        k = 3   # участников в турнире
        population = [generation.random_timeTable() for _ in range(POPULATION_SIZE)]
        count = 0
        t = Timer()
        start_best_fitness, info = generation.save_best_individ(population=population, k=0)  # сохранение лучшего индивида
        fitness_for_reduction_crossover = start_best_fitness // (P_CROSSOVER*100)     # через определенную приспоcобленность уменьшать шанс скрещивания
        poin_fitness_reduction_crossover = start_best_fitness-fitness_for_reduction_crossover     # отметка уменьшения скрещивания
        best_fitness = start_best_fitness
        # print(fitness_for_reduction_crossover, start_best_fitness, poin_fitness_reduction_crossover)
        while best_fitness >= 1:
            self.progress.emit(int((1-int(best_fitness)/int(start_best_fitness))*100))
            for ind1 in range(1, len(population)):    # скрещивание
                if random.random() < P_CROSSOVER:
                    # ind1, ind2 = random.sample(range(len(population)), 2)
                    ind2 = ind1-1
                    new_individ_1, new_individ_2 = generation.cxOrder(ind1=population[ind1].timeTable, ind2=population[ind2].timeTable)
                    individ = Individual(new_individ_1, generation.TimeTable_Fitness(new_individ_1), info='Скрещивание')
                    population.append(individ)
                    individ = Individual(new_individ_2, generation.TimeTable_Fitness(new_individ_2), info='Скрещивание')
                    population.append(individ)

            for i in range(len(population)):    # мутация
                if random.random() < P_MUTATION:
                    mutation_individ = generation.mutationTimeTable(population[i].timeTable)
                    individ = Individual(mutation_individ, generation.TimeTable_Fitness(mutation_individ), info='Мутация')
                    population.append(individ)

            best_fitness, info = generation.save_best_individ(population=population, k=3) # сохранение лучшего индивида
            population = generation.tournament_selection(population=population, k=k,  num_parents=POPULATION_SIZE)  # отбор
            count += 1

            if best_fitness < poin_fitness_reduction_crossover: # постепенно уменьшаем скрещивание, а мутацию увеличиваем тк под конец скрещивание не эффективно
                P_CROSSOVER -= 0.01
                P_MUTATION += 0.01
                # if P_CROSSOVER == 0 or P_MUTATION == 1 or P_MUTATION == 0.6:
                # print(round(P_MUTATION, 3), round(P_CROSSOVER, 3), round(best_fitness, 3), t.end())
                poin_fitness_reduction_crossover -= fitness_for_reduction_crossover
            # pass
            # if best_fitness <= 100 and P_CROSSOVER == 0.4:
            #     P_CROSSOVER = 0
            #     P_MUTATION = 0.6
            # if t.end() >= 31:
            #     index_min = min(range(len(population)), key=lambda i: population[i].fitness)
            #     min_individ = population[index_min]
            #     best_fitness = min_individ.fitness
            print('#', count, round(best_fitness, 3), t.end())

        print(t.end(), count)
        index_min = min(range(len(population)), key=lambda i: population[i].fitness)
        min_individ = population[index_min]
        # generation.save_TimeTable_in_DB(min_individ.timeTable)
        self.result.emit(generation.get_TimeTable_for_save(min_individ.timeTable))
        # self.progress.emit(100)

        #     middle_time += t.end()
        #     l = sorted([round(ind.fitness, 3) for ind in population])
        #     # print(l)
        #     middle_combined_lesson += l[0]
        # print(middle_time/n, 'ср. время', middle_combined_lesson/n, ' - ср. кол-во совмещенных пар')


# ga = startGA()

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

# 2500	186   	60  	139.35
# [[34, 47, 27, 24, 31, 6, 1, 21, 38, 39, 40, 30, 7, 8, 22, 46, 18, 36, 33, 12, 4, 2, 20, 26, 10, 29, 35, 14, 0, 32, 41, 37, 5, 23, 28, 25, 11, 45, 16, 43, 15, 44, 13, 19, 3, 17, 42, 9], [18, 28, 30, 6, 35, 16, 42, 38, 0, 7, 33, 40, 19, 47, 44, 4, 11, 34, 21, 32, 36, 12, 27, 8, 1, 31, 22, 13, 23, 43, 26, 14, 29, 17, 9, 10, 2, 46, 24, 37, 15, 20, 41, 5, 39, 25, 45, 3], [26, 21, 18, 43, 23, 39, 17, 13, 3, 40, 38, 34, 32, 7, 24, 2, 27, 1, 22, 6, 31, 29, 15, 9, 0, 19, 14, 28, 12, 45, 41, 35, 8, 44, 33, 47, 46, 20, 5, 11, 36, 4, 10, 37, 30, 16, 25, 42], [25, 34, 2, 5, 6, 30, 44, 12, 29, 22, 17, 3, 42, 7, 40, 1, 43, 20, 16, 33, 47, 41, 39, 21, 4, 27, 26, 10, 36, 18, 32, 38, 46, 24, 19, 8, 9, 23, 15, 31, 14, 28, 37, 35, 11, 0, 45, 13], [39, 22, 31, 2, 46, 47, 13, 6, 4, 10, 33, 40, 25, 34, 32, 3, 1, 17, 36, 24, 44, 38, 37, 18, 23, 5, 15, 8, 27, 26, 21, 12, 20, 28, 45, 43, 11, 7, 42, 29, 0, 9, 35, 30, 14, 41, 19, 16], [40, 30, 4, 1, 45, 21, 17, 26, 43, 39, 19, 28, 32, 34, 3, 8, 22, 18, 33, 42, 20, 9, 11, 24, 6, 10, 15, 38, 16, 31, 44, 41, 0, 36, 46, 7, 27, 12, 14, 23, 25, 35, 47, 29, 13, 37, 5, 2], [17, 28, 22, 16, 20, 47, 41, 9, 36, 26, 34, 3, 21, 0, 18, 4, 25, 27, 35, 19, 2, 11, 14, 12, 1, 42, 39, 44, 15, 10, 31, 6, 38, 5, 40, 8, 37, 43, 30, 24, 32, 45, 46, 33, 7, 23, 13, 29], [7, 21, 16, 36, 45, 27, 41, 10, 12, 19, 47, 33, 15, 28, 25, 26, 35, 14, 9, 8, 24, 29, 11, 6, 17, 18, 39, 31, 42, 23, 13, 37, 2, 44, 46, 38, 30, 4, 43, 0, 3, 34, 22, 32, 40, 5, 20, 1], [5, 13, 27, 44, 32, 39, 12, 40, 33, 15, 18, 42, 34, 21, 2, 11, 0, 35, 17, 4, 36, 16, 30, 1, 38, 28, 19, 8, 3, 22, 14, 9, 10, 41, 25, 45, 20, 6, 26, 7, 29, 23, 43, 31, 46, 37, 47, 24]]
# 60
# 653.3  секунд
#  5.0 - приспособленность в секунду
# 3881.2 139.35
# 3741.85

# на 846 поколении достигло 60
# 1000	187   	60  	142.2
# [[7, 13, 18, 5, 17, 30, 26, 9, 8, 22, 47, 38, 6, 43, 40, 45, 36, 31, 27, 15, 42, 28, 39, 41, 35, 1, 14, 10, 24, 0, 29, 3, 34, 4, 20, 11, 44, 32, 33, 2, 46, 23, 21, 37, 12, 19, 16, 25], [39, 21, 23, 7, 18, 20, 22, 6, 38, 29, 24, 9, 31, 25, 19, 42, 27, 16, 26, 1, 15, 8, 43, 4, 36, 30, 0, 11, 32, 17, 12, 3, 41, 46, 47, 34, 35, 45, 37, 28, 44, 5, 40, 10, 2, 33, 14, 13], [6, 28, 39, 18, 14, 34, 46, 36, 4, 47, 38, 7, 21, 19, 13, 24, 41, 2, 8, 32, 5, 45, 37, 29, 22, 23, 26, 1, 0, 33, 16, 43, 44, 20, 12, 30, 11, 31, 25, 42, 17, 10, 27, 9, 3, 40, 35, 15], [25, 19, 42, 30, 37, 43, 26, 5, 32, 14, 35, 20, 0, 38, 36, 2, 10, 4, 33, 45, 8, 34, 41, 24, 15, 12, 3, 7, 18, 40, 1, 6, 9, 22, 28, 13, 31, 44, 16, 21, 29, 27, 47, 23, 46, 17, 39, 11], [25, 6, 42, 10, 28, 15, 39, 38, 41, 21, 30, 16, 33, 26, 13, 36, 29, 4, 19, 0, 18, 43, 8, 3, 44, 46, 20, 24, 2, 9, 34, 14, 1, 45, 40, 5, 11, 22, 47, 7, 12, 32, 27, 31, 17, 35, 23, 37], [30, 37, 8, 9, 10, 25, 12, 14, 24, 22, 29, 6, 38, 17, 23, 32, 42, 11, 45, 2, 41, 28, 35, 15, 36, 47, 39, 40, 5, 4, 16, 33, 1, 46, 31, 20, 44, 13, 27, 0, 18, 34, 3, 7, 26, 19, 21, 43], [14, 43, 45, 20, 17, 42, 11, 34, 29, 33, 25, 15, 38, 28, 4, 7, 6, 24, 46, 1, 30, 36, 13, 5, 0, 8, 26, 19, 21, 39, 27, 31, 40, 18, 2, 10, 12, 16, 32, 22, 44, 9, 23, 3, 41, 35, 47, 37], [1, 36, 37, 26, 32, 16, 42, 45, 20, 21, 27, 35, 8, 5, 47, 41, 22, 34, 18, 31, 14, 43, 10, 4, 30, 33, 0, 9, 23, 28, 29, 25, 6, 24, 19, 11, 39, 38, 12, 3, 2, 40, 44, 7, 17, 46, 15, 13], [15, 7, 16, 9, 31, 4, 47, 8, 3, 41, 17, 2, 20, 45, 36, 38, 34, 46, 29, 28, 21, 25, 42, 18, 44, 13, 23, 30, 10, 6, 19, 43, 37, 22, 35, 12, 14, 33, 26, 32, 39, 0, 24, 5, 11, 27, 40, 1]]
# 60
# 262.7  секунд
#  14.0 - приспособленность в секунду
# 3881.0 142.2
# 3738.8
# gen	nevals	min	avg
# за 2000 поколений достигло 20
# 1000	191   	20 	106
# [[7, 13, 18, 5, 17, 30, 26, 9, 8, 22, 47, 38, 1, 43, 40, 45, 36, 21, 27, 15, 42, 28, 39, 0, 35, 6, 14, 10, 24, 2, 29, 3, 34, 4, 20, 11, 44, 32, 33, 41, 46, 23, 12, 37, 31, 19, 16, 25], [39, 21, 23, 7, 18, 20, 22, 24, 38, 28, 6, 9, 31, 25, 19, 42, 43, 16, 26, 1, 15, 8, 27, 4, 36, 30, 0, 11, 32, 17, 12, 3, 41, 46, 47, 34, 35, 45, 37, 29, 44, 5, 40, 10, 2, 33, 14, 13], [6, 28, 39, 18, 14, 34, 46, 36, 4, 47, 38, 7, 21, 19, 13, 24, 41, 2, 8, 32, 5, 45, 37, 29, 22, 23, 26, 1, 0, 33, 16, 43, 44, 20, 12, 30, 11, 31, 25, 42, 17, 10, 27, 9, 3, 40, 35, 15], [25, 19, 42, 30, 37, 43, 8, 5, 32, 14, 35, 20, 0, 12, 36, 2, 10, 4, 33, 45, 26, 34, 41, 24, 15, 38, 1, 7, 18, 40, 3, 6, 9, 22, 28, 13, 31, 44, 16, 21, 29, 27, 47, 23, 46, 17, 39, 11], [25, 6, 42, 10, 28, 15, 39, 38, 41, 21, 30, 8, 33, 26, 13, 36, 29, 7, 19, 0, 18, 43, 16, 3, 44, 46, 20, 24, 2, 9, 34, 14, 1, 45, 40, 5, 11, 22, 47, 4, 12, 32, 27, 31, 17, 35, 23, 37], [30, 37, 8, 9, 10, 25, 12, 14, 24, 22, 29, 6, 38, 17, 23, 32, 42, 11, 45, 2, 41, 28, 35, 15, 36, 47, 39, 40, 5, 4, 16, 33, 1, 46, 31, 20, 44, 13, 27, 0, 18, 34, 3, 7, 26, 19, 21, 43], [11, 43, 45, 20, 17, 42, 14, 34, 29, 33, 25, 15, 38, 28, 4, 7, 6, 24, 46, 1, 30, 36, 13, 2, 0, 8, 26, 19, 21, 39, 27, 31, 40, 18, 5, 10, 12, 16, 32, 22, 44, 9, 23, 3, 41, 35, 47, 37], [1, 36, 37, 26, 32, 16, 42, 11, 20, 21, 27, 35, 8, 5, 47, 41, 22, 34, 18, 31, 14, 43, 10, 4, 30, 33, 0, 9, 23, 28, 29, 25, 6, 24, 19, 45, 39, 38, 12, 3, 2, 40, 44, 7, 17, 46, 15, 13], [15, 7, 16, 9, 31, 4, 47, 8, 3, 41, 17, 2, 20, 45, 36, 38, 34, 46, 29, 28, 21, 25, 42, 18, 40, 13, 23, 30, 10, 6, 19, 43, 37, 22, 35, 12, 14, 33, 26, 32, 39, 0, 24, 5, 11, 27, 44, 1]]
# 20
# 267.16  секунд
#  0.0 - приспособленность в секунду
# 142.2 106.0
# 36.19999999999999
# за 5к поколений так и осталось на 20


# увеличил мутацию особи с 0.2 до 0.3 и за 985 поколений дошло до нуля
# 1000	182   	0   	144.95
# [[25, 46, 39, 42, 1, 47, 19, 22, 8, 2, 24, 27, 5, 0, 14, 21, 35, 28, 43, 38, 7, 40, 23, 20, 30, 33, 18, 44, 37, 15, 16, 45, 34, 3, 13, 9, 11, 10, 31, 36, 17, 29, 32, 12, 41, 26, 6, 4], [1, 14, 44, 13, 12, 11, 38, 8, 37, 45, 19, 10, 0, 24, 28, 32, 35, 23, 43, 18, 40, 15, 47, 4, 6, 16, 17, 33, 21, 31, 26, 36, 25, 20, 29, 7, 5, 46, 39, 22, 34, 3, 42, 9, 2, 27, 30, 41], [40, 41, 30, 4, 0, 35, 32, 18, 45, 26, 43, 34, 44, 22, 10, 2, 23, 29, 31, 6, 25, 16, 42, 8, 33, 13, 37, 28, 46, 36, 3, 5, 15, 27, 17, 11, 12, 38, 14, 20, 24, 9, 21, 7, 47, 19, 39, 1], [29, 31, 41, 13, 42, 4, 36, 7, 37, 35, 40, 22, 11, 8, 20, 25, 6, 46, 15, 14, 34, 26, 38, 5, 1, 3, 12, 27, 30, 43, 19, 39, 17, 23, 28, 0, 2, 9, 16, 45, 32, 24, 44, 10, 18, 33, 47, 21], [19, 29, 45, 36, 42, 17, 23, 2, 7, 0, 28, 39, 31, 30, 47, 15, 27, 9, 32, 4, 1, 40, 44, 16, 8, 3, 21, 34, 26, 20, 38, 11, 22, 46, 43, 41, 12, 14, 33, 25, 6, 37, 35, 5, 10, 13, 24, 18], [43, 47, 20, 34, 19, 27, 39, 38, 26, 18, 1, 0, 32, 21, 36, 10, 9, 15, 16, 24, 7, 2, 29, 44, 12, 37, 17, 3, 46, 25, 23, 41, 33, 35, 42, 4, 30, 31, 8, 5, 22, 40, 6, 11, 45, 13, 14, 28], [34, 19, 2, 0, 42, 29, 9, 4, 11, 27, 37, 40, 24, 41, 31, 10, 36, 45, 17, 30, 20, 39, 14, 13, 18, 23, 7, 3, 15, 43, 25, 5, 33, 44, 22, 28, 26, 8, 12, 1, 16, 21, 32, 35, 6, 47, 38, 46], [13, 24, 18, 40, 36, 31, 19, 8, 45, 22, 20, 34, 11, 29, 23, 37, 25, 17, 1, 6, 3, 27, 42, 0, 43, 44, 32, 33, 7, 39, 38, 21, 4, 5, 30, 41, 10, 47, 28, 14, 35, 26, 15, 16, 9, 2, 12, 46], [2, 8, 37, 24, 23, 27, 12, 19, 14, 44, 13, 42, 16, 18, 47, 43, 5, 32, 40, 3, 46, 4, 38, 0, 33, 17, 39, 9, 21, 30, 25, 11, 20, 45, 35, 10, 26, 22, 34, 15, 1, 7, 31, 28, 36, 41, 29, 6]]
# 0
# 266.77  секунд
#  14.0 - приспособленность в секунду
# 3901.4 144.95
# 3756.4500000000003

# уменьшил мутацию группы с 0.25 до 0.2 и за 1000 поколений дошло до 40
# 1000	184   	40  	148.55
# [[0, 33, 40, 47, 28, 42, 16, 37, 38, 29, 3, 5, 6, 20, 24, 45, 41, 13, 11, 7, 12, 22, 25, 44, 32, 34, 35, 46, 2, 14, 21, 26, 8, 17, 31, 1, 10, 4, 19, 23, 39, 30, 27, 15, 9, 43, 36, 18], [1, 34, 31, 9, 20, 26, 37, 15, 19, 33, 46, 42, 41, 22, 25, 7, 0, 27, 45, 36, 6, 21, 38, 10, 14, 32, 17, 12, 8, 29, 24, 13, 44, 39, 16, 28, 40, 3, 23, 2, 4, 30, 18, 5, 11, 47, 43, 35], [20, 15, 16, 38, 8, 7, 45, 37, 42, 32, 29, 10, 4, 26, 36, 27, 2, 46, 24, 23, 25, 35, 21, 5, 1, 0, 39, 33, 3, 22, 9, 17, 13, 19, 30, 34, 18, 43, 40, 14, 47, 44, 31, 6, 11, 12, 41, 28], [17, 32, 13, 2, 47, 28, 41, 40, 35, 43, 39, 11, 37, 24, 46, 44, 7, 6, 15, 29, 5, 0, 38, 31, 8, 14, 18, 19, 23, 10, 16, 9, 21, 30, 45, 3, 25, 27, 42, 36, 22, 34, 1, 4, 12, 33, 26, 20], [15, 27, 7, 5, 33, 0, 11, 25, 22, 30, 16, 42, 46, 31, 18, 36, 38, 26, 32, 10, 43, 47, 24, 2, 3, 20, 40, 13, 44, 29, 37, 39, 35, 34, 45, 28, 4, 41, 12, 8, 17, 23, 14, 1, 9, 21, 19, 6], [1, 21, 28, 29, 35, 42, 20, 3, 23, 16, 9, 0, 18, 32, 11, 10, 17, 34, 37, 13, 31, 47, 43, 45, 27, 22, 44, 30, 2, 5, 19, 40, 6, 46, 36, 38, 33, 14, 4, 8, 7, 15, 26, 24, 39, 25, 12, 41], [45, 22, 27, 19, 10, 13, 38, 25, 8, 21, 40, 43, 6, 7, 39, 14, 11, 24, 41, 30, 5, 35, 26, 46, 4, 29, 20, 47, 28, 17, 33, 3, 0, 9, 16, 42, 34, 23, 44, 32, 1, 37, 36, 18, 2, 12, 15, 31], [13, 28, 6, 11, 41, 20, 33, 14, 15, 9, 31, 7, 19, 12, 44, 40, 4, 10, 22, 26, 27, 37, 18, 47, 38, 24, 29, 25, 2, 43, 32, 16, 42, 17, 34, 23, 3, 35, 36, 45, 39, 0, 46, 5, 1, 21, 30, 8], [44, 17, 1, 3, 13, 39, 18, 10, 21, 23, 40, 41, 2, 36, 19, 30, 4, 26, 37, 33, 25, 45, 14, 5, 31, 0, 43, 7, 9, 24, 15, 8, 38, 16, 47, 42, 46, 34, 28, 22, 6, 20, 29, 35, 32, 27, 12, 11]]
# 40
# 272.23  секунд
#  13.0 - приспособленность в секунду
# 3890.45 148.55
# 3741.8999999999996

#  мутацией группы 0.3 достигло 160 за 1к
# 1000	181   	160 	297.4
# [[32, 25, 26, 16, 8, 37, 18, 11, 41, 47, 40, 28, 21, 20, 7, 1, 17, 39, 45, 22, 46, 27, 42, 14, 2, 12, 38, 35, 5, 30, 15, 43, 0, 3, 36, 29, 33, 13, 34, 10, 4, 31, 23, 44, 24, 19, 6, 9], [29, 45, 43, 28, 37, 47, 22, 4, 2, 1, 17, 32, 24, 27, 15, 23, 21, 36, 5, 0, 31, 42, 41, 11, 8, 3, 25, 14, 20, 39, 46, 30, 10, 9, 26, 40, 34, 33, 19, 13, 16, 7, 12, 6, 18, 44, 38, 35], [24, 35, 41, 23, 13, 2, 8, 15, 40, 29, 20, 18, 3, 43, 39, 45, 4, 36, 31, 12, 5, 14, 32, 1, 26, 21, 44, 38, 25, 0, 37, 9, 22, 28, 47, 10, 19, 33, 27, 6, 34, 46, 16, 30, 17, 7, 11, 42], [34, 38, 35, 11, 8, 12, 16, 17, 6, 40, 31, 7, 4, 1, 43, 37, 33, 18, 14, 13, 26, 21, 44, 19, 22, 42, 29, 46, 41, 9, 45, 0, 25, 32, 3, 10, 47, 28, 24, 39, 30, 27, 2, 5, 36, 23, 15, 20], [43, 37, 18, 34, 4, 38, 46, 15, 30, 40, 27, 17, 44, 0, 41, 12, 26, 7, 19, 11, 2, 9, 31, 16, 5, 10, 21, 22, 13, 47, 36, 6, 25, 1, 3, 23, 28, 29, 39, 24, 45, 33, 14, 35, 32, 42, 20, 8], [39, 13, 28, 8, 33, 15, 27, 43, 10, 20, 18, 40, 24, 29, 21, 2, 42, 3, 35, 9, 1, 44, 19, 38, 17, 25, 16, 32, 30, 47, 46, 14, 37, 34, 5, 4, 22, 0, 12, 11, 7, 6, 41, 36, 31, 23, 26, 45], [6, 28, 18, 19, 5, 24, 16, 43, 26, 34, 20, 23, 3, 9, 31, 30, 1, 21, 36, 37, 29, 41, 10, 4, 39, 32, 46, 14, 0, 38, 47, 27, 45, 15, 22, 8, 40, 44, 17, 35, 12, 7, 33, 11, 2, 42, 13, 25], [10, 28, 47, 21, 22, 34, 33, 16, 30, 32, 2, 42, 25, 1, 44, 3, 17, 35, 4, 5, 12, 14, 39, 13, 0, 20, 36, 27, 11, 6, 38, 46, 9, 40, 18, 19, 29, 24, 23, 8, 26, 43, 45, 7, 15, 41, 31, 37], [7, 1, 45, 28, 27, 21, 36, 37, 15, 4, 47, 0, 39, 14, 20, 12, 44, 24, 34, 8, 13, 25, 11, 3, 33, 31, 18, 9, 10, 22, 17, 42, 29, 41, 30, 43, 5, 19, 40, 46, 35, 32, 2, 26, 6, 16, 38, 23]]
# 160
# 268.35  секунд
#  13.0 - приспособленность в секунду
# 3895.1 297.4
# 3597.7

#  мутацией группы 0.25 достигло 40 за 746
# 1000	191   	40  	214.9
# [[23, 44, 4, 10, 0, 31, 37, 45, 16, 34, 43, 24, 3, 32, 15, 19, 29, 2, 41, 6, 12, 35, 39, 38, 8, 11, 36, 13, 28, 20, 22, 1, 17, 18, 26, 7, 40, 42, 33, 21, 9, 25, 14, 27, 5, 46, 47, 30], [24, 19, 18, 36, 11, 38, 41, 22, 9, 33, 23, 30, 4, 40, 45, 3, 21, 46, 25, 29, 34, 0, 43, 10, 28, 12, 15, 1, 42, 27, 44, 39, 16, 17, 47, 7, 32, 26, 37, 31, 35, 2, 20, 8, 14, 5, 13, 6], [1, 29, 23, 20, 39, 36, 17, 31, 32, 34, 35, 4, 2, 41, 21, 15, 30, 7, 40, 5, 42, 25, 44, 0, 38, 24, 14, 37, 13, 47, 27, 22, 43, 45, 16, 12, 19, 26, 11, 9, 10, 8, 46, 18, 3, 28, 33, 6], [42, 24, 41, 34, 43, 46, 21, 19, 37, 15, 47, 1, 32, 27, 45, 9, 39, 6, 18, 2, 17, 20, 4, 10, 36, 14, 30, 5, 16, 28, 33, 3, 26, 13, 31, 0, 8, 11, 38, 12, 29, 44, 35, 7, 25, 40, 23, 22], [10, 38, 13, 45, 6, 23, 32, 28, 44, 20, 30, 1, 14, 21, 34, 18, 19, 0, 17, 4, 7, 40, 29, 24, 35, 26, 39, 37, 11, 36, 25, 27, 31, 33, 16, 3, 46, 9, 22, 8, 12, 41, 2, 5, 47, 15, 43, 42], [31, 44, 30, 12, 27, 25, 37, 11, 23, 43, 47, 0, 6, 9, 14, 22, 28, 13, 21, 38, 20, 42, 1, 2, 19, 29, 41, 40, 36, 4, 35, 10, 46, 32, 16, 3, 45, 17, 15, 39, 5, 24, 26, 18, 33, 8, 34, 7], [46, 44, 36, 39, 11, 41, 20, 0, 23, 13, 34, 18, 6, 9, 35, 37, 3, 43, 12, 21, 28, 38, 14, 2, 10, 7, 17, 25, 40, 24, 15, 22, 45, 5, 8, 32, 31, 30, 33, 26, 47, 27, 42, 1, 4, 19, 29, 16], [19, 35, 24, 0, 16, 8, 10, 41, 20, 36, 14, 1, 37, 47, 32, 44, 11, 17, 25, 13, 3, 38, 43, 42, 40, 4, 26, 9, 46, 18, 33, 45, 2, 39, 31, 5, 29, 30, 23, 22, 34, 21, 15, 27, 12, 6, 28, 7], [45, 16, 38, 47, 7, 18, 32, 22, 37, 34, 28, 21, 13, 27, 39, 11, 19, 36, 0, 5, 6, 41, 26, 4, 2, 12, 35, 17, 31, 24, 10, 8, 29, 9, 46, 1, 33, 20, 15, 3, 42, 14, 30, 44, 40, 23, 25, 43]]
# 40
# 262.71  секунд
#  14.0 - приспособленность в секунду
# 3900.5 214.9
# 3685.6

# с мутацией группы 0.15 достигло 20 за 390 поколений (0 был на 600, но его стерли)
# 1000	185   	20  	92.1
# [[7, 28, 14, 37, 21, 41, 19, 44, 24, 1, 35, 5, 43, 47, 22, 29, 4, 6, 45, 31, 0, 20, 27, 12, 10, 9, 32, 18, 38, 13, 33, 26, 25, 23, 36, 2, 17, 39, 34, 11, 46, 40, 16, 3, 30, 15, 42, 8], [0, 16, 28, 23, 4, 6, 46, 17, 24, 13, 15, 42, 33, 38, 1, 8, 10, 37, 18, 12, 34, 39, 30, 35, 20, 26, 14, 22, 3, 41, 32, 2, 27, 11, 44, 7, 25, 19, 36, 5, 29, 45, 47, 40, 9, 21, 43, 31], [43, 9, 18, 1, 47, 25, 35, 8, 37, 36, 29, 3, 32, 41, 38, 6, 45, 44, 42, 34, 23, 17, 12, 4, 13, 27, 31, 15, 30, 39, 21, 22, 0, 40, 16, 11, 2, 26, 20, 7, 5, 24, 19, 28, 46, 33, 14, 10], [4, 40, 21, 5, 3, 15, 42, 34, 35, 19, 36, 37, 11, 0, 31, 33, 2, 13, 25, 29, 39, 22, 47, 41, 45, 12, 9, 7, 38, 16, 46, 6, 32, 20, 23, 1, 8, 17, 44, 43, 24, 14, 28, 27, 18, 30, 26, 10], [36, 47, 46, 45, 38, 30, 22, 8, 37, 21, 15, 17, 0, 19, 26, 14, 32, 25, 1, 4, 18, 29, 5, 6, 33, 35, 7, 2, 9, 20, 28, 34, 11, 39, 40, 3, 23, 13, 12, 41, 10, 24, 43, 27, 42, 16, 31, 44], [0, 12, 17, 25, 31, 38, 1, 2, 10, 23, 43, 30, 44, 21, 29, 22, 28, 6, 4, 16, 26, 42, 46, 24, 20, 14, 33, 41, 5, 27, 19, 32, 7, 13, 39, 36, 8, 18, 34, 11, 3, 40, 45, 37, 47, 35, 15, 9], [31, 19, 42, 10, 21, 12, 47, 45, 9, 6, 28, 27, 5, 46, 15, 35, 23, 24, 14, 41, 1, 20, 38, 11, 22, 29, 0, 3, 7, 30, 16, 25, 2, 36, 39, 40, 37, 34, 32, 44, 33, 43, 17, 18, 26, 4, 13, 8], [10, 3, 22, 21, 7, 27, 43, 35, 6, 9, 15, 36, 19, 16, 24, 11, 37, 45, 41, 30, 44, 17, 32, 39, 2, 46, 18, 14, 25, 47, 8, 5, 28, 40, 13, 29, 1, 42, 20, 38, 0, 26, 31, 4, 12, 34, 23, 33], [42, 31, 32, 39, 43, 16, 9, 0, 3, 13, 26, 7, 23, 44, 22, 12, 18, 27, 41, 10, 11, 45, 21, 29, 35, 2, 37, 8, 1, 34, 46, 24, 17, 19, 38, 14, 28, 20, 25, 30, 4, 15, 36, 33, 5, 40, 47, 6]]
# 20
# 270.57  секунд
#  13.0 - приспособленность в секунду
# 3848.95 92.1
# 3756.85

# с мутацией группы 0.15 достигло 0 за 503 поколений
# 1000	192   	0   	77.9
# [[30, 9, 23, 4, 36, 25, 46, 43, 28, 24, 44, 37, 10, 47, 13, 2, 41, 35, 1, 0, 38, 40, 20, 21, 17, 34, 16, 11, 33, 39, 22, 6, 7, 5, 45, 42, 8, 3, 12, 18, 27, 19, 15, 32, 29, 31, 14, 26], [38, 43, 36, 14, 7, 15, 30, 32, 11, 42, 33, 31, 27, 18, 39, 13, 19, 40, 9, 8, 35, 6, 41, 2, 25, 22, 26, 34, 24, 23, 5, 10, 3, 17, 20, 12, 37, 21, 46, 1, 47, 44, 29, 0, 28, 16, 45, 4], [28, 34, 43, 8, 1, 29, 37, 10, 44, 47, 18, 0, 31, 12, 45, 42, 32, 19, 15, 3, 2, 39, 16, 30, 25, 38, 5, 6, 46, 14, 40, 26, 11, 23, 35, 21, 36, 41, 4, 9, 20, 17, 27, 7, 33, 24, 22, 13], [21, 23, 14, 46, 28, 18, 19, 13, 34, 16, 43, 5, 3, 38, 20, 36, 25, 2, 15, 10, 30, 37, 11, 1, 4, 39, 40, 8, 22, 35, 42, 29, 17, 32, 31, 47, 12, 44, 24, 33, 9, 6, 45, 26, 7, 41, 27, 0], [45, 36, 19, 0, 42, 10, 25, 7, 18, 39, 28, 12, 9, 15, 27, 35, 43, 26, 41, 4, 3, 33, 13, 16, 2, 14, 34, 6, 11, 8, 29, 24, 5, 46, 38, 1, 23, 17, 22, 47, 31, 32, 44, 21, 37, 20, 40, 30], [33, 23, 36, 9, 18, 35, 46, 1, 21, 25, 24, 10, 40, 29, 13, 3, 11, 42, 39, 0, 20, 47, 32, 41, 17, 38, 6, 8, 27, 14, 19, 44, 43, 34, 37, 2, 5, 30, 12, 22, 31, 45, 26, 15, 7, 4, 28, 16], [43, 31, 36, 8, 14, 41, 24, 29, 35, 9, 12, 11, 32, 2, 42, 5, 21, 18, 16, 6, 15, 20, 27, 40, 39, 47, 28, 22, 1, 30, 37, 13, 4, 38, 19, 7, 0, 17, 44, 46, 10, 3, 26, 34, 23, 45, 33, 25], [47, 41, 44, 18, 1, 14, 21, 34, 9, 32, 26, 39, 10, 11, 33, 19, 4, 31, 22, 27, 37, 24, 43, 7, 8, 36, 17, 23, 35, 12, 25, 5, 29, 38, 45, 6, 40, 42, 46, 30, 13, 28, 3, 0, 16, 20, 15, 2], [34, 27, 37, 40, 9, 39, 15, 21, 11, 28, 22, 30, 19, 35, 5, 2, 23, 12, 36, 38, 7, 10, 41, 25, 33, 13, 31, 26, 18, 8, 20, 0, 3, 16, 42, 43, 47, 32, 45, 44, 4, 14, 29, 46, 1, 6, 24, 17]]
# 0
# 277.16  секунд
#  13.0 - приспособленность в секунду
# 3839.35 77.9
# 3761.45


# с популяцией в 100 застряло на 40 (2к поколений)
# 1000	92    	40 	126.4
# [[8, 3, 41, 44, 29, 45, 20, 6, 34, 27, 38, 7, 31, 42, 28, 46, 36, 32, 16, 12, 47, 21, 11, 1, 33, 13, 19, 22, 24, 25, 14, 40, 2, 17, 15, 35, 4, 30, 18, 5, 10, 0, 39, 23, 37, 43, 26, 9], [6, 33, 22, 23, 35, 21, 12, 28, 18, 43, 2, 1, 32, 13, 36, 8, 4, 16, 47, 3, 46, 38, 27, 15, 24, 0, 44, 7, 31, 19, 30, 40, 14, 25, 29, 17, 41, 39, 9, 5, 10, 26, 45, 37, 20, 42, 34, 11], [24, 40, 13, 3, 9, 5, 45, 47, 2, 41, 12, 28, 8, 26, 39, 7, 34, 20, 30, 42, 19, 32, 15, 35, 16, 21, 22, 23, 11, 4, 29, 25, 10, 38, 33, 1, 6, 46, 31, 0, 43, 37, 44, 17, 18, 27, 36, 14], [35, 29, 39, 0, 20, 19, 34, 38, 13, 22, 43, 15, 9, 7, 47, 24, 12, 21, 26, 4, 30, 44, 8, 3, 6, 25, 42, 33, 16, 36, 17, 45, 37, 31, 18, 41, 32, 14, 1, 2, 10, 23, 28, 27, 40, 11, 46, 5], [36, 17, 30, 34, 35, 14, 26, 0, 15, 16, 42, 6, 43, 3, 23, 4, 24, 10, 46, 7, 38, 12, 33, 44, 21, 28, 32, 47, 11, 45, 39, 1, 18, 25, 31, 27, 22, 20, 29, 19, 40, 13, 8, 5, 41, 37, 9, 2], [0, 44, 42, 1, 10, 13, 47, 12, 20, 5, 7, 14, 38, 37, 26, 46, 33, 31, 27, 29, 21, 22, 36, 8, 6, 43, 19, 23, 15, 30, 40, 16, 28, 9, 39, 4, 41, 35, 32, 11, 18, 34, 17, 45, 3, 24, 25, 2], [34, 43, 31, 2, 23, 44, 38, 45, 47, 15, 5, 10, 36, 12, 13, 14, 27, 16, 29, 6, 40, 8, 11, 37, 26, 1, 46, 0, 32, 22, 33, 28, 25, 41, 35, 3, 17, 9, 19, 7, 18, 21, 39, 4, 30, 24, 20, 42], [2, 19, 23, 40, 46, 39, 30, 37, 38, 3, 21, 7, 6, 35, 20, 28, 26, 33, 31, 14, 29, 10, 34, 8, 18, 41, 12, 42, 32, 16, 17, 15, 1, 4, 22, 13, 5, 43, 24, 44, 11, 47, 25, 45, 0, 36, 27, 9], [2, 3, 20, 27, 33, 32, 41, 13, 47, 24, 9, 5, 34, 44, 46, 35, 21, 16, 42, 1, 4, 43, 22, 40, 36, 7, 38, 6, 0, 39, 31, 14, 19, 12, 17, 10, 37, 30, 45, 11, 25, 28, 29, 26, 8, 15, 18, 23]]
# 40
# 136.24  секунд * 2
#  -1.0 - приспособленность в секунду
# 113.5 126.4
# -12.900000000000006


# популяция 300 застряло на 40 (500 поколений)
# 500	281   	40  	124.633
# [[8, 28, 19, 7, 32, 21, 45, 35, 37, 26, 34, 25, 1, 11, 38, 43, 39, 47, 15, 5, 4, 27, 17, 33, 31, 22, 29, 3, 23, 0, 14, 6, 2, 18, 40, 10, 42, 20, 24, 36, 30, 16, 44, 9, 13, 41, 46, 12], [21, 24, 6, 2, 18, 38, 3, 9, 1, 40, 41, 20, 17, 39, 12, 28, 7, 45, 25, 31, 36, 32, 22, 29, 13, 14, 47, 44, 34, 11, 23, 4, 19, 27, 42, 0, 26, 5, 37, 8, 46, 30, 43, 16, 10, 33, 35, 15], [0, 40, 45, 47, 5, 18, 19, 38, 10, 21, 43, 44, 25, 32, 24, 14, 3, 36, 46, 22, 23, 17, 2, 9, 26, 27, 12, 42, 1, 16, 35, 33, 11, 37, 28, 7, 39, 34, 41, 13, 8, 30, 20, 31, 29, 15, 4, 6], [26, 46, 23, 0, 12, 29, 35, 44, 1, 39, 36, 41, 30, 42, 11, 9, 19, 13, 20, 32, 38, 2, 16, 4, 31, 15, 6, 5, 18, 3, 43, 10, 22, 28, 21, 45, 34, 24, 37, 14, 8, 27, 17, 7, 25, 33, 40, 47], [34, 22, 18, 32, 16, 26, 31, 17, 41, 8, 11, 30, 4, 5, 42, 37, 13, 40, 14, 29, 19, 21, 2, 10, 46, 23, 39, 43, 27, 35, 7, 1, 6, 3, 28, 24, 0, 15, 25, 45, 38, 20, 36, 9, 12, 47, 44, 33], [14, 25, 35, 32, 4, 36, 47, 16, 22, 43, 5, 8, 9, 18, 24, 15, 46, 29, 26, 10, 40, 41, 39, 7, 19, 27, 21, 3, 44, 42, 13, 23, 34, 28, 12, 45, 31, 0, 1, 38, 37, 2, 33, 6, 11, 20, 30, 17], [2, 46, 44, 16, 8, 10, 31, 13, 39, 40, 35, 5, 28, 32, 36, 30, 27, 1, 33, 4, 34, 37, 29, 24, 9, 17, 25, 19, 43, 14, 42, 3, 0, 15, 45, 41, 21, 12, 38, 23, 7, 11, 26, 18, 6, 47, 22, 20], [17, 18, 33, 1, 2, 7, 31, 29, 23, 20, 32, 40, 35, 16, 46, 6, 39, 34, 4, 3, 41, 26, 15, 36, 45, 47, 27, 10, 22, 24, 5, 0, 37, 38, 12, 9, 11, 43, 44, 21, 19, 30, 14, 8, 25, 13, 28, 42], [16, 6, 35, 2, 47, 22, 34, 38, 20, 44, 29, 23, 18, 43, 26, 3, 9, 13, 32, 21, 15, 41, 1, 0, 19, 12, 45, 4, 11, 36, 39, 7, 17, 25, 42, 28, 24, 46, 33, 10, 14, 40, 8, 5, 37, 27, 31, 30]]
# 40
# 208.05  секунд
#  18.0 - приспособленность в секунду
# 3916.6666666666665 124.63333333333334
# 3792.0333333333333

# 0.15, популяция 200
# 1000	185   	20  	103.7
# [[15, 25, 44, 16, 46, 24, 31, 41, 7, 45, 22, 30, 18, 23, 5, 1, 20, 43, 21, 6, 11, 9, 19, 37, 42, 29, 13, 34, 28, 12, 4, 2, 33, 35, 40, 3, 39, 10, 38, 8, 32, 14, 17, 26, 36, 27, 47, 0], [18, 17, 31, 20, 7, 12, 21, 10, 6, 25, 15, 33, 23, 2, 36, 8, 43, 42, 24, 26, 3, 35, 47, 39, 9, 13, 46, 44, 37, 29, 27, 34, 11, 45, 14, 22, 38, 30, 40, 19, 41, 28, 1, 5, 32, 0, 16, 4], [47, 20, 19, 5, 23, 29, 7, 10, 30, 39, 15, 12, 2, 36, 22, 18, 46, 24, 42, 4, 26, 13, 31, 8, 44, 17, 41, 1, 3, 37, 38, 43, 32, 35, 27, 34, 14, 0, 21, 11, 9, 45, 16, 6, 40, 25, 28, 33], [13, 32, 6, 5, 14, 10, 26, 8, 0, 12, 27, 45, 42, 38, 28, 20, 30, 16, 41, 34, 31, 29, 46, 3, 18, 33, 15, 37, 9, 22, 43, 23, 44, 36, 47, 19, 1, 11, 35, 40, 25, 7, 21, 2, 4, 17, 39, 24], [7, 44, 29, 32, 45, 13, 40, 14, 42, 18, 30, 1, 38, 20, 39, 5, 10, 36, 28, 21, 25, 19, 8, 4, 3, 23, 15, 26, 6, 47, 34, 11, 43, 17, 12, 33, 31, 27, 0, 9, 37, 22, 46, 35, 2, 41, 24, 16], [45, 3, 20, 5, 1, 30, 29, 14, 28, 47, 39, 31, 2, 26, 38, 24, 33, 34, 11, 4, 27, 43, 19, 18, 12, 15, 16, 41, 9, 10, 21, 23, 46, 22, 17, 40, 0, 42, 37, 35, 36, 8, 25, 6, 7, 13, 32, 44], [45, 21, 44, 14, 27, 30, 39, 47, 32, 41, 20, 4, 11, 3, 40, 31, 5, 10, 17, 33, 8, 43, 16, 29, 1, 7, 26, 23, 25, 36, 24, 18, 0, 12, 42, 37, 15, 35, 34, 6, 13, 28, 19, 38, 22, 46, 2, 9], [11, 15, 19, 10, 20, 4, 7, 38, 31, 37, 33, 30, 16, 34, 14, 8, 5, 39, 44, 47, 27, 32, 42, 41, 6, 3, 40, 17, 18, 43, 36, 22, 24, 35, 2, 1, 25, 23, 21, 9, 0, 26, 28, 13, 46, 45, 12, 29], [10, 45, 28, 32, 7, 41, 22, 30, 4, 2, 29, 44, 11, 23, 43, 46, 31, 17, 24, 25, 9, 20, 16, 12, 47, 13, 0, 1, 34, 27, 19, 5, 37, 15, 40, 35, 3, 8, 33, 18, 6, 38, 42, 14, 36, 26, 21, 39]]
# 20
# 267.31  секунд
#  14.0 - приспособленность в секунду
# 3923.85 103.7
# 3820.15

# достиг 20 на 1к и по итогу 3к поколений так на 20 и остался (возможно стоит сделать скрещивание рандомным)

# сделал скрещивание более рандомным
# до 0 дошло за 604	поколения
# [[10, 4, 47, 28, 24, 36, 19, 3, 6, 37, 12, 23, 17, 34, 22, 1, 5, 35, 29, 26, 13, 40, 45, 30, 43, 38, 46, 11, 14, 16, 20, 31, 2, 25, 27, 8, 42, 39, 15, 33, 41, 7, 32, 0, 18, 44, 21, 9], [26, 36, 13, 21, 9, 37, 34, 16, 46, 35, 38, 5, 30, 41, 17, 11, 6, 39, 23, 15, 2, 28, 12, 1, 8, 19, 40, 14, 32, 44, 31, 33, 27, 3, 29, 4, 43, 45, 47, 10, 22, 42, 20, 25, 0, 18, 24, 7], [38, 43, 24, 29, 6, 25, 46, 47, 34, 8, 26, 2, 33, 16, 37, 42, 5, 19, 32, 22, 11, 44, 39, 3, 12, 7, 23, 1, 21, 28, 40, 14, 15, 31, 30, 9, 45, 36, 35, 18, 20, 13, 4, 0, 27, 17, 41, 10], [33, 38, 3, 8, 0, 2, 30, 40, 13, 25, 43, 27, 15, 47, 23, 35, 42, 41, 20, 22, 5, 7, 32, 31, 11, 17, 19, 24, 26, 18, 4, 6, 1, 28, 37, 36, 14, 44, 16, 45, 9, 12, 39, 46, 34, 21, 29, 10], [29, 33, 40, 5, 32, 26, 28, 2, 46, 18, 37, 19, 20, 24, 41, 4, 0, 11, 43, 35, 31, 25, 12, 3, 7, 15, 30, 39, 13, 34, 36, 10, 8, 9, 14, 22, 38, 27, 45, 23, 47, 44, 16, 17, 1, 42, 21, 6], [13, 12, 45, 11, 41, 33, 3, 5, 27, 38, 4, 9, 0, 18, 44, 26, 34, 43, 21, 36, 32, 29, 25, 37, 8, 47, 31, 20, 42, 23, 10, 7, 6, 16, 39, 15, 19, 14, 35, 17, 28, 30, 22, 24, 1, 46, 40, 2], [10, 31, 16, 5, 43, 20, 8, 7, 36, 25, 33, 3, 28, 45, 26, 40, 14, 35, 21, 11, 30, 19, 24, 22, 41, 34, 17, 2, 37, 13, 29, 38, 46, 18, 47, 6, 0, 4, 15, 42, 32, 39, 12, 23, 44, 27, 1, 9], [8, 31, 44, 19, 9, 47, 45, 43, 28, 36, 26, 40, 11, 24, 17, 7, 6, 34, 46, 21, 13, 33, 23, 4, 42, 16, 38, 18, 29, 0, 41, 2, 27, 37, 32, 25, 22, 12, 30, 39, 15, 35, 10, 3, 1, 5, 14, 20], [0, 32, 16, 8, 33, 43, 1, 6, 31, 44, 22, 19, 42, 41, 38, 30, 5, 13, 45, 17, 10, 27, 12, 34, 3, 11, 20, 26, 21, 35, 29, 23, 7, 2, 15, 46, 39, 14, 9, 4, 24, 28, 40, 25, 18, 37, 36, 47]]
# 0
# 269.85  секунд
#  14.0 - приспособленность в секунду
# 3892.95 90.2
# 3802.75

# до 0 дошло за 501

# 0 на 271 мутация 0.4
# 500	195   	0   	102.75
# [[34, 43, 40, 16, 3, 30, 17, 22, 1, 27, 28, 18, 5, 25, 47, 19, 2, 10, 26, 13, 4, 39, 15, 12, 31, 38, 23, 33, 42, 0, 21, 11, 6, 44, 36, 45, 35, 24, 14, 37, 46, 20, 32, 7, 8, 41, 29, 9], [10, 7, 14, 16, 0, 8, 27, 26, 41, 21, 33, 37, 3, 35, 36, 25, 17, 24, 38, 47, 30, 31, 32, 5, 43, 23, 40, 12, 4, 28, 44, 46, 34, 29, 18, 22, 9, 19, 20, 45, 13, 6, 42, 1, 2, 15, 39, 11], [24, 19, 27, 21, 3, 0, 34, 16, 11, 42, 12, 30, 32, 14, 17, 15, 36, 25, 4, 6, 39, 47, 37, 7, 1, 13, 31, 22, 23, 44, 29, 28, 40, 33, 45, 2, 9, 18, 46, 5, 26, 41, 38, 20, 43, 8, 35, 10], [27, 19, 18, 12, 6, 45, 37, 5, 31, 32, 16, 22, 39, 17, 35, 43, 11, 46, 36, 4, 3, 8, 20, 23, 33, 42, 2, 10, 29, 25, 40, 47, 14, 15, 24, 9, 38, 44, 13, 30, 21, 7, 26, 1, 28, 41, 34, 0], [18, 29, 45, 10, 37, 21, 19, 15, 25, 39, 34, 6, 8, 35, 14, 41, 5, 12, 47, 44, 17, 0, 24, 1, 43, 40, 38, 7, 28, 42, 46, 27, 31, 26, 23, 32, 13, 30, 16, 4, 2, 3, 33, 22, 11, 9, 20, 36], [34, 38, 5, 2, 42, 17, 9, 0, 19, 26, 39, 22, 10, 14, 27, 16, 31, 35, 20, 24, 3, 25, 44, 40, 41, 12, 47, 7, 8, 18, 36, 23, 43, 45, 32, 46, 6, 28, 21, 1, 30, 13, 15, 37, 33, 29, 11, 4], [1, 29, 43, 37, 13, 2, 12, 0, 38, 19, 18, 45, 21, 16, 24, 4, 7, 40, 17, 44, 8, 32, 14, 36, 11, 31, 39, 33, 22, 6, 20, 10, 35, 23, 15, 42, 5, 9, 41, 25, 3, 30, 47, 28, 34, 46, 26, 27], [16, 19, 14, 11, 43, 44, 40, 39, 15, 32, 5, 0, 24, 35, 10, 4, 13, 27, 20, 38, 29, 28, 42, 9, 3, 33, 46, 45, 6, 1, 17, 22, 25, 34, 36, 37, 26, 18, 31, 8, 23, 30, 21, 12, 7, 2, 47, 41], [8, 30, 14, 21, 3, 25, 16, 42, 6, 9, 33, 23, 18, 26, 37, 35, 27, 22, 47, 29, 28, 2, 24, 11, 44, 19, 38, 32, 46, 10, 40, 5, 15, 43, 20, 0, 45, 12, 41, 17, 4, 13, 39, 36, 34, 31, 1, 7]]
# 0
# 91.01  секунд
#  42.0 - приспособленность в секунду
# 3935.45 102.75
# 3832.7

# мутация 0.4 0 на 490
# 500 за 100.53  секунд


# 4000	178   	0.65   	126.025 c
# [[29, 15, 12, 4, 19, 35, 36, 38, 42, 32, 33, 9, 31, 18, 7, 11, 3, 24, 13, 1, 27, 20, 44, 45, 26, 14, 46, 16, 17, 37, 34, 39, 41, 30, 23, 10, 28, 47, 5, 8, 6, 25, 21, 0, 2, 22, 40, 43], [6, 31, 24, 22, 19, 45, 12, 36, 8, 34, 37, 30, 3, 9, 27, 42, 11, 46, 21, 33, 17, 41, 35, 7, 15, 26, 25, 23, 18, 43, 13, 38, 20, 32, 4, 10, 40, 14, 28, 44, 2, 47, 29, 5, 16, 39, 0, 1], [12, 35, 5, 0, 16, 14, 39, 23, 47, 21, 31, 34, 4, 44, 13, 24, 7, 38, 28, 19, 10, 3, 27, 45, 1, 33, 36, 32, 6, 11, 41, 29, 42, 20, 22, 17, 9, 2, 15, 25, 8, 37, 30, 18, 43, 40, 26, 46], [43, 15, 19, 12, 38, 42, 46, 2, 14, 41, 8, 7, 40, 27, 35, 25, 23, 29, 9, 6, 0, 26, 32, 20, 47, 16, 18, 11, 1, 44, 45, 21, 13, 39, 4, 5, 3, 28, 37, 24, 22, 31, 34, 10, 36, 30, 33, 17], [10, 14, 31, 11, 27, 42, 25, 43, 1, 34, 26, 46, 30, 35, 37, 6, 40, 24, 33, 4, 20, 16, 22, 2, 9, 13, 32, 5, 28, 12, 29, 45, 0, 3, 44, 47, 8, 7, 36, 18, 41, 38, 23, 21, 19, 17, 39, 15], [32, 42, 6, 4, 11, 2, 20, 34, 24, 44, 22, 21, 15, 23, 43, 35, 45, 17, 40, 12, 29, 37, 1, 10, 27, 41, 36, 26, 7, 9, 19, 33, 25, 18, 3, 5, 14, 30, 0, 8, 46, 16, 38, 13, 28, 39, 47, 31], [16, 36, 33, 34, 18, 21, 15, 39, 42, 29, 4, 5, 28, 32, 31, 1, 0, 44, 19, 38, 27, 14, 7, 8, 10, 11, 43, 35, 17, 20, 47, 6, 41, 46, 45, 25, 2, 9, 23, 12, 3, 40, 30, 37, 26, 13, 22, 24], [1, 8, 45, 20, 4, 43, 33, 38, 39, 18, 5, 3, 29, 13, 34, 46, 9, 14, 24, 28, 21, 25, 12, 36, 16, 26, 2, 10, 44, 41, 32, 35, 6, 17, 42, 11, 0, 7, 37, 47, 19, 15, 23, 27, 22, 30, 31, 40], [31, 46, 23, 9, 41, 38, 27, 10, 14, 29, 17, 11, 18, 28, 22, 43, 37, 32, 1, 6, 12, 39, 45, 3, 30, 47, 24, 8, 42, 36, 16, 0, 15, 21, 19, 7, 5, 26, 20, 44, 35, 34, 13, 2, 33, 40, 25, 4]]
# 0.6500000000000004
# 722.91  секунд
#  5.0 - приспособленность в секунду
# 3941.838050000011 126.02514999999993
# 3815.8129000000113

# 1000	191   	45  	199.8   добавил ограничение для учителей (без окон и минимум 2 пары (или 0))
# [[10, 14, 45, 4, 6, 2, 41, 37, 7, 19, 20, 35, 16, 40, 17, 9, 12, 29, 18, 44, 36, 28, 13, 21, 3, 22, 42, 30, 39, 26, 46, 0, 47, 27, 15, 32, 8, 24, 38, 43, 5, 23, 34, 11, 1, 25, 31, 33], [5, 46, 17, 45, 27, 28, 12, 18, 22, 19, 38, 2, 7, 40, 47, 11, 36, 15, 41, 0, 25, 35, 44, 10, 13, 34, 31, 37, 6, 16, 24, 30, 21, 43, 39, 42, 4, 33, 14, 9, 1, 8, 23, 32, 3, 29, 26, 20], [2, 36, 41, 30, 26, 45, 8, 4, 7, 12, 23, 15, 42, 16, 17, 24, 20, 35, 40, 33, 47, 13, 1, 5, 9, 3, 39, 22, 28, 31, 21, 0, 29, 32, 25, 14, 19, 37, 34, 44, 27, 38, 10, 11, 6, 46, 18, 43], [15, 46, 32, 36, 34, 28, 6, 0, 45, 33, 44, 18, 19, 20, 29, 26, 2, 7, 43, 12, 3, 30, 42, 8, 37, 31, 1, 10, 17, 35, 21, 13, 9, 14, 47, 22, 23, 16, 39, 5, 11, 38, 24, 25, 4, 40, 27, 41], [1, 29, 19, 44, 2, 33, 36, 4, 7, 21, 34, 22, 11, 12, 37, 45, 31, 43, 42, 17, 5, 47, 32, 41, 35, 13, 25, 23, 46, 16, 28, 0, 15, 40, 9, 8, 39, 14, 18, 30, 10, 24, 20, 26, 6, 3, 38, 27], [11, 7, 32, 42, 29, 16, 24, 41, 34, 35, 26, 13, 47, 38, 3, 0, 46, 39, 30, 44, 10, 1, 45, 25, 21, 14, 40, 36, 4, 5, 27, 18, 33, 17, 9, 6, 23, 37, 20, 8, 2, 22, 43, 19, 31, 12, 15, 28], [26, 27, 2, 5, 46, 28, 24, 29, 9, 35, 13, 33, 10, 36, 34, 16, 38, 22, 12, 30, 17, 15, 1, 11, 47, 40, 3, 8, 32, 18, 7, 6, 19, 39, 45, 31, 4, 0, 37, 25, 44, 41, 42, 43, 21, 23, 14, 20], [2, 42, 13, 45, 25, 23, 15, 41, 11, 19, 20, 12, 0, 9, 34, 36, 38, 16, 1, 3, 32, 28, 24, 47, 7, 40, 27, 44, 22, 43, 4, 10, 26, 29, 39, 8, 21, 33, 6, 5, 18, 17, 35, 14, 46, 37, 30, 31], [16, 3, 10, 39, 22, 37, 32, 38, 7, 8, 35, 43, 11, 31, 30, 20, 25, 41, 34, 24, 26, 46, 27, 2, 18, 33, 29, 45, 12, 13, 19, 40, 4, 1, 21, 47, 17, 44, 36, 28, 6, 42, 23, 5, 0, 9, 14, 15]]
# 45
# 198.7  секунд
#  21.0 - приспособленность в секунду
# 4442.35 199.8
# 4242.55
# далее за 4к застряло на 10


# 1000	190   	5   	61.875 мутация 0.5 0.5 0.01
# [[5, 1, 34, 33, 17, 35, 47, 3, 36, 19, 41, 7, 0, 8, 14, 28, 29, 23, 22, 30, 15, 38, 45, 40, 37, 39, 26, 25, 9, 21, 18, 44, 10, 4, 16, 13, 11, 31, 12, 6, 2, 20, 32, 43, 24, 27, 46, 42], [5, 28, 40, 23, 45, 46, 13, 0, 44, 19, 15, 26, 10, 29, 20, 8, 42, 14, 32, 41, 17, 38, 7, 4, 25, 27, 18, 39, 3, 35, 37, 34, 2, 30, 31, 11, 43, 16, 33, 22, 6, 21, 24, 9, 1, 36, 47, 12], [10, 1, 14, 27, 15, 21, 18, 17, 7, 40, 24, 41, 3, 43, 31, 46, 39, 37, 11, 8, 30, 28, 45, 42, 13, 38, 4, 6, 47, 16, 5, 2, 26, 19, 44, 25, 12, 22, 9, 0, 32, 35, 36, 33, 29, 23, 34, 20], [20, 24, 7, 3, 45, 43, 28, 30, 6, 38, 47, 5, 42, 13, 27, 29, 9, 1, 44, 36, 18, 34, 15, 37, 0, 21, 22, 16, 31, 33, 17, 23, 39, 40, 25, 35, 11, 4, 19, 32, 8, 10, 26, 14, 2, 12, 41, 46], [16, 18, 39, 12, 6, 8, 25, 36, 44, 14, 26, 38, 23, 32, 47, 3, 10, 31, 21, 1, 42, 20, 17, 0, 27, 15, 2, 4, 37, 43, 40, 33, 11, 7, 29, 13, 34, 35, 28, 19, 5, 41, 22, 46, 24, 30, 45, 9], [1, 31, 40, 16, 21, 26, 5, 6, 22, 30, 24, 19, 13, 36, 20, 35, 0, 8, 25, 14, 9, 42, 34, 29, 11, 4, 44, 43, 15, 38, 3, 10, 7, 18, 17, 2, 23, 47, 41, 45, 12, 37, 39, 32, 46, 27, 33, 28], [29, 37, 26, 40, 27, 34, 13, 16, 23, 24, 47, 35, 9, 7, 14, 15, 4, 3, 28, 25, 1, 11, 41, 33, 8, 38, 42, 45, 31, 17, 5, 6, 43, 12, 19, 39, 0, 30, 18, 36, 46, 44, 20, 10, 2, 21, 22, 32], [4, 40, 38, 39, 6, 31, 44, 46, 12, 33, 34, 32, 3, 36, 37, 25, 18, 45, 10, 8, 7, 35, 30, 26, 0, 5, 15, 22, 14, 29, 42, 27, 1, 43, 41, 23, 24, 13, 21, 20, 2, 11, 16, 28, 9, 47, 17, 19], [5, 18, 22, 10, 28, 17, 12, 7, 20, 36, 41, 11, 34, 33, 23, 46, 47, 38, 35, 43, 37, 15, 0, 6, 45, 24, 3, 4, 32, 40, 14, 13, 26, 42, 29, 39, 8, 30, 44, 19, 9, 1, 16, 31, 21, 27, 25, 2]]
# 5
# 198.39  секунд
#  21.0 - приспособленность в секунду
# 4390.075 61.875
# 4328.2

# 0.7 0.1 0.01
# пуляция 150 за 1200


# сохранение 3 лучших
# с постепенным уменьшением скрещивания, 0.2 - мутация, 0.4 - скрещивание
# 50 - ср. 278.6 сек
#  182.11 3031
#  180.93 3073
#  215.48 3673
#  452.5 7707
#  364.73 5577

# 70 - ср. 236 сек
#  249.41 3471
#  240.85 3385
#  193.37 2717
#  164.15 2371
#  334.11 4949

# 90 - ср. 221.6 сек
#  253.03 3896
#  182.5 2855
#  285.11 4419
#  256.46 3964
#  132.24 2012

# 110 - ср. 210.4 сек
#  164.05 2530
#  177.89 2769
#  243.08 3686
#  190.34 2711
#  278.27 3990

# 110
# 52 148.6 2443
# 52 226.37 3779
# 52 257.96 4180
# 52 189.47 3129
# 52 380.76 6412
# 240.632 ср. время 0.1252  - ср. кол-во совмещенных пар

# 130
# 52 425.28 7044
# 52 170.19 2820
# 52 136.31 2299
# 52 221.41 3591
# 52 149.07 2436
# 220.452 ср. время 0.12940000000000002  - ср. кол-во совмещенных пар

# 150
# 52 159.81 2632
# 52 380.71 6365
# 52 158.51 2469
# 52 171.57 2863
# 52 151.22 2624
# 204.36399999999998 ср. время 0.1286  - ср. кол-во совмещенных пар

# 170
# 52 202.92 3541
# 52 198.98 2976
# 52 275.55 4332
# 52 341.3 5008
# 52 633.54 9321
# 330.45799999999997 ср. время 0.11979999999999999  - ср. кол-во совмещенных пар



# 70
# 289.9 4362
# 310.55 4740
# 166.63 2626
# 222.04 3592
# 405.45 6511
# 1118.93 17892
# 1001.61 15931
# 281.11 4484
# 230.64 3655
# 282.13 4680
# 861.798//2 ср. время 0.238  - ср. кол-во совмещенных пар
# 90
# 109.43 2027
# 1334.53 25072
# 205.63 3858
# 253.77 3983
# 136.14 2535
# 157.6 2606
# 286.82 4874
# 419.84 7213
# 229.4 3912
# 382.41 6597
# 703.114//2 ср. время 0.2544  - ср. кол-во совмещенных пар
# 110
# 157.84 2727
# 319.53 5645
# 175.74 3281
# 102.8 1902
# 280.1 5252
# 237.12 4447
# 129.05 2403
# 227.05 4260
# 181.68 3397
# 196.83 3689
# 401.548//2 ср. время 0.26180000000000003  - ср. кол-во совмещенных пар


# 70
# 473.74 8687
# 371.38 6890
# 157.54 2905
# 632.7 11763
# 1333.11 24813
# 198.04 3658
# 191.36 3536
# 347.57 6455
# 247.45 4581
# 683.9 12724
# 463.679 ср. время 0.11840000000000002  - ср. кол-во совмещенных пар
# 90
# 134.36 2477
# 153.72 2837
# 296.63 5500
# 321.03 5944
# 174.73 3226
# 1422.3 26487
# 151.83 2798
# 141.22 2599
# 485.31 9006
# 202.07 3723
# 348.32 ср. время 0.1251  - ср. кол-во совмещенных пар
# 110
# 545.91 10138
# 186.57 3440
# 416.49 7731
# 222.46 4101
# 103.7 1902
# 161.75 2983
# 214.6 3966
# 673.81 12520
# 776.87 14446
# 194.53 3589
# 349.669 ср. время 0.12010000000000001  - ср. кол-во совмещенных пар
# 130
# 766.15 14259
# 148.19 2729
# 179.94 3314
# 241.07 4460
# 320.53 5935
# 667.96 12403
# 527.8 9792
# 119.48 2193
# 387.58 7186
# 251.49 4656
# 361.01900000000006 ср. время 0.12050000000000001  - ср. кол-во совмещенных пар
# 150
# 188.28 3474
# 284.54 5265
# 665.39 12351
# 234.63 4294
# 369.25 6837
# 1206.2 22409
# 135.04 2483
# 193.23 3560
# 136.8 2513
# 147.47 2716
# 356.08299999999997 ср. время 0.1257  - ср. кол-во совмещенных пар


# 100
# 109.85 3241
# 124.3 3617
# 191.6 5864
# 204.26 5856
# 140.86 3600
# 141.81 3158
# 1791.14 40263
# 937.81 22291
# 299.98 7844
# 174.38 4827
# 411.599 ср. время 0.12159999999999997  - ср. кол-во совмещенных пар

# 100   (ошибка была в постепенном уменьшении)
# 124.45 3646
# 89.42 2562
# 71.27 2038
# 129.71 3794
# 225.82 6703
# 128.13400000000001 ср. время 0.133  - ср. кол-во совмещенных пар


# 50
# 389.69 9379
# 255.24 6835
# 496.17 13076
# 1182.29 32111
# 433.21 11935
# 70
# 125.16 3279
# 164.18 4076
# 110.2 2658
# 219.59 5779
# 162.87 4250
# 90
# 309.65 8371
# 293.48 8111
# 798.91 21040
# 217.25 5540
# 85.13 2168
# 110
# 298.78 7734
# 839.37 20922
# 113.35 2642
# 899.42 24413
# 180.96 4517
# 130

# 61566 0.088 2826.24
# 2826.24 61566

# 18108 0.099 772.37
# 772.37 18108
