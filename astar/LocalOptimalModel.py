# coding:utf-8
# @Author: wangye
# @Description: consider the next hour weather,and try to find the path out
#               of the dangerous zone which is the optimal postion to the end
# @Date:Created  on 20:36 2018/1/30.
# @Modify
# ======================shaun=======================================
import math
import random
from astar import HashAstar
from astar.HashAstar import Node

X_DIM = 548
Y_DIM = 421
HOUR_STEP = 30
RANGE = 6
DELTA_ANGLE = 30
NUM_LIMIT = 3
TRY_ANGLES_CNT = 12
TRY_RANGE = 6


# 该模型基本思路是以下一时次为好天的
class LocalOptimalModel:
    tryFind = 0

    def __init__(self):
        self.tryFind = 0

    def findOptimalZone(self, hourIdx, now, end, maps, atimes, rtimes):
        if atimes > TRY_ANGLES_CNT or rtimes > TRY_RANGE:
            return None
        self.tryFind += 1
        seta = math.atan((end.y - now.y) / (now.y - now.x))
        minAlpha = seta - (DELTA_ANGLE * atimes / 2 * (math.pi / 180))
        maxAlpha = seta + (DELTA_ANGLE * atimes / 2 * (math.pi / 180))
        zone = []
        for r in range(HOUR_STEP - RANGE * rtimes, HOUR_STEP + 1, 1):
            for talpha in range(int(minAlpha * 10000), int(maxAlpha * 10000),
                                int(round(math.asin(1.0 / (HOUR_STEP - RANGE * (rtimes - 1))) * 10000))):
                alpha = talpha / 10000.
                if 0 <= int(r * round(math.sin(alpha))) + now.x < X_DIM and 0 <= int(
                                r * round(math.cos(alpha))) + now.y < Y_DIM:
                    node = HashAstar.Node(int(r * round(math.cos(alpha))) + now.x,
                                          int(r * round(math.sin(alpha))) + now.y)
                    zone.append(node)
        rzone = list(set(zone))
        nextMap = maps[hourIdx + 1]
        for node in rzone:
            if nextMap[node.x, node.y] > 0:
                rzone.remove(node)
        if len(rzone) > NUM_LIMIT:
            return rzone
        else:
            if atimes == rtimes:
                self.findOptimalZone(self, hourIdx, now, end, maps, atimes + 1, rtimes)
            else:
                self.findOptimalZone(self, hourIdx, now, end, maps, atimes, rtimes + 1)

    def sortedDictKeys(self, adict):
        keys = adict.keys()
        keys.sort()
        t = map(adict.get, keys)
        return t

    # 主要程序
    def doFindPath(self, hourIdx, now, end, maps):
        aims = self.findOptimalZone(hourIdx, now, end, maps, 1, 1)
        curMap = maps[hourIdx]
        for aim in aims:
            startPoint = HashAstar.Node(now.x, now.y)
            endPoint = HashAstar.Node(aim.x, aim.y)
            startPoint.__setCost__(0)
            # A-star寻路
            HashAstar.init()
            node = HashAstar.astarMainLoop(startPoint, endPoint, curMap)
            if not node:
                continue
            if node.__eq__(endPoint):
                return node
            if node.__selfCostFunction__() < HOUR_STEP:
                tmpNode = None
                for ii in range(node.__selfCostFunction__(), HOUR_STEP):
                    tNode = Node(node.x, node.y)
                    if tmpNode:
                        tNode.__setParent__(node)
                        tNode.cost = node.__selfCostFunction__ + 1
                        tmpNode = tNode
                    else:
                        tNode.__setParent__(tmpNode)
                        tNode.cost = tmpNode.__selfCostFunction__ + 1
                        tmpNode = tNode
                return node
        return None
