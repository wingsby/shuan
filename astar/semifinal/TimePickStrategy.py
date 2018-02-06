# coding:utf-8
# @Author: wangye
# @Description: new alogrithm for semi final
# @Date:Created  on 23:19 2018/2/5.
# @Modify
# ======================shaun=======================================
# -*- coding: utf-8 -*-

import os
import sys
from datetime import *

import numpy as np
import pandas as pd
import astar.Tools as Tools


class City:
    baseCity = None

    def __init__(self, array):
        self.id = array[0]
        self.x = array[1]
        self.y = array[2]

    def distance(self):
        if self.baseCity:
            return abs(self.x - self.baseCity.x) + abs(self.y - self.baseCity.y)

    def getXRanges(self):
        if self.x < self.baseCity.x:
            return [self.x, self.baseCity.x]
        else:
            return [self.baseCity.x, self.x]

    def getYRanges(self):
        if self.y < self.baseCity.y:
            return [self.y, self.baseCity.y]
        else:
            return [self.baseCity.y, self.y]

    # 第二方案
    def getXRanges2(self):
        if self.x - 30 >= 0:
            sx = self.x - 30
        else:
            sx = 0
        if self.x + 30 < 548:
            ex = self.x + 30
        else:
            ex = 548
        return [sx, ex]

    def getYRanges2(self):
        if self.y - 30 >= 0:
            sy = self.y - 30
        else:
            sy = 0
        if self.y + 30 < 421:
            ey = self.y + 30
        else:
            ey = 420
        return [sy, ey]

    @classmethod
    def setBaseCity(cls, city):
        cls.baseCity = city


def decideTimePickStrategy(maps):
    # 给出各城市
    # filePath = "E:\\machineLearningData\\shaun\\"
    filePath = "F:\\ml\\data\\"
    citys = pd.read_csv(filePath + "CityData.csv")
    cityArray = citys.values
    cityMap = dict()
    baseCity = City(cityArray[0])
    City.setBaseCity(baseCity)
    for array in cityArray:
        ctmp = City(array)
        cityMap[ctmp.id] = ctmp

    # 计算方区内障碍比
    # 修改为起点及终点障碍比，60*60方格

    timeMap = dict()
    poseedTime = dict()
    # 城市id
    for i in range(1, 11):
        city = cityMap.get(i)
        list = []
        for hourIdx in range(0, 18):
            curMap = maps[hourIdx]
            sliceMap = curMap[city.getXRanges()[0]:city.getXRanges()[1],
                       city.getYRanges()[0]:city.getYRanges()[1]]
            cnt = len(sliceMap[sliceMap >= 1])
            list.append(cnt)
        dis = city.distance()
        time = int(round((dis * 2. / 60) * 1.2 ))
        if time > 18:
            time = 18
        tmpdict = dict()
        # 临时写法
        minsum = 99999
        mincnt = -1
        for j in range(0, len(list) - time):
            sum = 0
            for k in range(0, time):
                sum += list[k]
                # tmpdict.put(j, sum)
                # 排序求出最少的组合
            if minsum > sum:
                minsum = sum
                mint = j

        for tt in range(0, 100, 10):
            if tt < 60:
                stime = (mint + 3) * 100 + tt
            else:
                stime = (mint + 4) * 100 + tt - 60
            if not poseedTime.has_key(stime):
                poseedTime[stime] = i
                timeMap[i] = stime
                break
    return timeMap
