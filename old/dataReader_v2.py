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
    hours = range(3, 21)
    days = range(6, 11)
    filePath = None

    @classmethod
    def setMapes(cls):
        fname = cls.filePath + "/" + "ForecastDataforTesting_ensmean.csv"
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

    def getMaps(self):
        maps = []
        for hour in range(3, 21):
            map = self.mapes[self.day * 100 + hour]
            map[map < self.threshold] = 0
            map[map >= self.threshold] = 1
            maps.append(map)
        return maps


def savePath(node, id, day):
    fileName = dataReader.filePath + "/routSave.csv"
    fileWriter = open(fileName, "a")

    nnode = []
    nnode.append(node)
    # todo 可以优化代码吗 多余的循环
    tmpNode = node.parent
    while tmpNode:
        nnode.append(tmpNode)
        tmpNode = tmpNode.parent
    for i in range(len(nnode) - 1, -1, -1):
        # fileWriter.write(
        #     "%d,%d,%s,%d,%d\n" % (id, day, generateTime(node.__selfCostFunction__()), nnode.x + 1, node.y + 1))
        # curNode = node.parent
        # while curNode:
        fileWriter.write(
            "%d,%d,%s,%d,%d\n" % (
                id, day, generateTime(nnode[i].__selfCostFunction__()), nnode[i].x + 1, nnode[i].y + 1))
        # curNode = curNode.parent
    fileWriter.close()


def generateTime(steps):
    addHour = steps * 2 / 60
    addMinute = steps * 2 % 60
    return "%02d:%02d" % (3 + addHour, addMinute)


def regressAstar(startPoint, endPoint, map):
    # 各小时map
    HashAstar.init()
    node = HashAstar.astarMainLoop(startPoint, endPoint, map[0])
    if not node:
        return None
    newStart, hourIdx = checkNode(node, map, 3, 0)
    nnode = None
    list=[]
    # if newStart
    while  newStart:
        list = addToList(list, newStart)
        HashAstar.init()
        if hourIdx < 0:
            break
        # newStart
        nnode = HashAstar.astarMainLoop(newStart, endPoint, map[hourIdx])
        # 链表长度
        newStart, hourIdx = checkNode(nnode, map, 3, len(list))
    if nnode:
        return nnode
    else:
        return node


def addToList(list, node):
    # 拼接节点
    if not node:
        return None
    curNode = node.parent
    newlist = []
    newlist.append(node)
    while curNode:
        newlist.append(curNode)
        curNode = node.parent
    if len(list) > 0:
        joinNode = list.get(len(list) - 1)
        list.remove(joinNode)
        node.setParent(joinNode.parent)
    for i in range(len(newlist) - 2, -1, -1):
        list.append(newlist[i])
    return list


def checkNode(node, mapes, delta, steps):
    # 重排node
    nnode = []
    nnode.append(node)
    # todo 可以优化代码吗 多余的循环
    tmpNode = node.parent
    while tmpNode:
        nnode.append(tmpNode)
        tmpNode = tmpNode.parent
    for i in range(len(nnode) - 1, -1, -1):
        hourIdx = int((nnode[i].__selfCostFunction__() + steps) / 30)
        if hourIdx > 2:
            pass
            # print(hourIdx)
        curMap = mapes[hourIdx]
        if curMap[nnode[i].x][nnode[i].y] == 1:
            cNode = nnode[i]
            for j in (0, delta):
                cNode = cNode.parent
            return cNode, hourIdx
    return None, -1


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
        for day in range(6, 11):
            reader = dataReader(day, 3)
            endPoint = HashAstar.Node(citys[target][1] - 1, citys[target][2] - 1)
            startPoint.__setCost__(0)
            start = time.time()
            maps = reader.getMaps()
            HashAstar.init()
            node = HashAstar.astarMainLoop(startPoint, endPoint, map)
            # node = regressAstar(startPoint, endPoint, maps)
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
