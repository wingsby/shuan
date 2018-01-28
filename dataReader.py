# coding:utf-8
# @Author: wangye
# @Description: set worldmap and read data
# @Date:Created  on 16:53 2018/1/28.
# @Modify
# ======================shaun=======================================
import numpy as np
import pandas as pd
import time
import os

from astar import HashAstar, plottest


class dataReader:
    threshold = 15
    mapes = dict()
    hours = range(3, 22)
    days = range(1, 6)
    filePath = None

    @classmethod
    def setMapes(cls):
        fname = cls.filePath + "/" + "ForecastDataforTraining_ensmean.csv"
        data = pd.read_csv(fname, iterator=True)
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

    @classmethod
    def getCityData(cls):
        fname = cls.filePath + "/" + "CityData.csv"
        data = pd.read_csv(fname)
        # data.close()
        return data.values

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


def savePath(node, id, day):
    fileName = dataReader.filePath + "/routSave.csv"
    fileWriter = open(fileName, "a")
    fileWriter.write(
        "%d,%d,%s,%d,%d\n" % (id, day, generateTime(node.__selfCostFunction__()), node.x + 1, node.y + 1))
    curNode = node.parent
    while curNode:
        fileWriter.write(
            "%d,%d,%s,%d,%d\n" % (id, day, generateTime(curNode.__selfCostFunction__()), curNode.x + 1, curNode.y + 1))
        curNode = curNode.parent
    fileWriter.close()


def generateTime(steps):
    addHour = steps * 2 / 60
    addMinute = steps * 2 % 60
    return "%02d:%02d" % (3 + addHour, addMinute)


if __name__ == "__main__":
    dataReader.filePath = "I:\python work\shuan\pancy"
    fileName = dataReader.filePath + "/routSave.csv"
    if os.path.exists(fileName):
        os.remove(fileName)
    citys = dataReader.getCityData()
    start = time.time()
    dataReader.setMapes()
    print("读取数据耗时：%d" % (time.time() - start))
    startPoint = HashAstar.Node(citys[0][1] - 1, citys[0][2] - 1)
    count = 0
    for target in range(1, 11):
        for day in range(1, 6):
            reader = dataReader(day, 7)
            endPoint = HashAstar.Node(citys[target][1] - 1, citys[target][2] - 1)
            startPoint.__setCost__(0)
            start = time.time()
            map = reader.getMap()
            HashAstar.init()
            node = HashAstar.astarMainLoop(startPoint, endPoint, map)
            print("耗时：%d 秒" % (time.time() - start))
            if not node:
                count += 1
                print("%d 架飞机寻路失败===================================\n========================" % (count))
                continue
            try:
                print("路径长度: %d" % node.__selfCostFunction__())
                savePath(node, target, day)
                # plottest.drawRoute(map, node, startPoint)
            except IOError as p:
                print(p.message)
