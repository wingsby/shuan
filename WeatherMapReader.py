# coding:utf-8
import pandas as pd
import numpy as np

class WeatherMapReader:
    threshold = 15
    mapes = dict()
    hours = range(3, 21)
    days = range(6, 11) #to do change days
    fileName = None

    @classmethod
    def setMapes(cls):
        data = pd.read_csv(cls.fileName, iterator=True)
        for day in cls.days:
            for hour in cls.hours:
                cls.read(day, hour, data)
        data.close()

    @classmethod
    def read(cls, day, hour, data):
        chunkSize = 230708
        try:
            tmp = data.get_chunk(chunkSize)
            cls.mapes[day * 100 + hour] = np.array(tmp['wind'].values).reshape(548, 421)
        except StopIteration:
            print("Iteration is stopped.")

    def __init__(self, day, hour):
        self.day = day
        self.hour = hour
        # self.weatherMap = np.zeros((548, 421))

    def convertMap(self):
        self.weatherMap[self.weatherMap < self.threshold] = 0
        self.weatherMap[self.weatherMap >= self.threshold] = 1
        return self.weatherMap

    def getMap(self):
        self.weatherMap = self.mapes[self.day * 100 + self.hour]
        return self.convertMap()

    def getMaps(self):
        maps = []
        for hour in range(3, 21):
            map = self.mapes[self.day * 100 + hour]
            map[map < self.threshold] = 0
            map[map >= self.threshold] = 1
            maps.append(map)
        return maps