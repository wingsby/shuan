import os
import sys
from datetime import *

import numpy as np
import pandas as pd
import Tools


class city:
    baseCity = None

    def __init__(self, array):
        self.id = array[0]
        self.x = array[1]
        self.y = array[2]

    def distance(self):
        if not baseCity:
            return abs(self.x - baseCity.x) + abs(self.y - baseCity.y)

    def getXRanges(self):
        if self.x < baseCity.x:
            return [self.x, baseCity.x]
        else:
            return [baseCity.x, self.x]

    def getYRanges(self):
        if self.y < baseCity.y:
            return [self.y, baseCity.y]
        else:
            return [baseCity.y, self.y]

    @classmethod
    def setBaseCity(cls, city):
        cls.baseCity = city


# 给出各城市
filePath = "E:\\machineLearningData\\shaun\\"
citys = pd.read_csv(filePath + "CityData.csv")
cityArray = city.values
cityMap = dict()
baseCity = city(cityArray[0])
city.setBaseCity(baseCity)
for array in cityArray:
    ctmp = city(array)
    cityMap.put(ctmp.id, ctmp)

# 计算方区内障碍比
timeMap = dict()
for i in range(1, 11):
    city = cityMap.get(i)
    list = ()
    for hourIdx in range(0, 18):
        curMap = maps[hourIdx]
        sliceMap = curMap[city.getXRanges()[0]:city.getXRanges()[1],
                   city.getYRanges()[0]:city.getYRanges()[1]]
        cnt = len(sliceMap[sliceMap >= 1])
        list.append(cnt)
    dis = city.distance()
    time = round((dis * 2. / 60) * 1.5 + 1)
    for j in list:
        sum = 0
        for k in range(0, time + 1):
            sum += list[k]
            #排序求出最少的组合
