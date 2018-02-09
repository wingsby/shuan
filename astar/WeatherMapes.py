# coding:utf-8
import pandas as pd
import numpy as np
import copy

from astar import Tools


class WeatherMapContainer:
    threshold = 15
    rthre = 4
    __mapes = dict()
    __weatherMapes = dict()
    __rmapes = dict()
    __hours = range(3, 21)
    __days = range(6, 11)  # to do change days
    fileName = None
    mapsFlag = False

    @classmethod
    def initWeatherMapes(cls):
        data = pd.read_csv(cls.fileName, iterator=True)
        for day in cls.__days:
            for hour in cls.__hours:
                cls.__read(day, hour, data)
        data.close()
        cls.__convertMapes()

    @classmethod
    def reproduceWeatherMapes(cls):
        cls.__convertMapes

    @classmethod
    def __convertMapes(cls):
        for day in cls.__days:
            for hour in cls.__hours:
                tmp = copy.copy(cls.__mapes.get(day * 100 + hour))
                rtmp = copy.copy(cls.__rmapes.get(day * 100 + hour))
                tmp[tmp >= cls.threshold] = -1
                tmp[rtmp >= cls.rthre] = -1
                tmp[tmp >= 0] = 0
                tmp[tmp < 0] = 1
                cls.__weatherMapes[day * 100 + hour] = tmp

    @classmethod
    def __read(cls, day, hour, data):
        chunkSize = 230708
        try:
            tmp = data.get_chunk(chunkSize)
            cls.__mapes[day * 100 + hour] = np.array(tmp['wind'].values).reshape(548, 421)
            cls.__rmapes[day * 100 + hour] = np.array(tmp['rain'].values).reshape(548, 421)
        except StopIteration:
            print("Iteration is stopped.")

    @classmethod
    def getWeatherMapes(cls, day):
        tmpList = []
        for hour in cls.__hours:
            tmp = copy.copy(cls.__weatherMapes[day * 100 + hour])
            tmpList.append(tmp)
        return tmpList

    @classmethod
    def getWeatherMap(cls, day, hour):
        tmp = copy.copy(cls.__weatherMapes[day * 100 + hour])
        return tmp
