# -*- coding: utf-8 -*-
# @Author: wangye
# @Description:
# @Date:Created  on 23:27 2018/1/27.
# @Modify
#
import numpy as np
import math


class Node:
    __hash__ = object.__hash__
    worldMap = []
    start = None
    end = None

    def __init__(self, xi, yi):
        self.x = int(xi)
        self.y = int(yi)
        self.parent = None
        # g cost
        self.cost = -1
        self.dis = -1

    # G 当前代价
    def __selfCostFunction__(self):
        if self.cost >= 0:
            return self.cost
        else:
            self.cost = self.parent.cost + 1
            return self.parent.cost + 1

    # 曼哈顿距离
    def distance(self, next):
        self.dis = abs(next.x - self.x) + abs(next.y - self.y)
        return self.dis

    # F = G + H 估计代价未知
    def __costFunction__(self):
        g = self.__selfCostFunction__()
        h = self.distance(self.end)
        return g + h

    def __eq__(self, other):
        if other.x == self.x and other.y == self.y:
            return True
        else:
            return False

    # get the up left down right
    def fetchNeibours(self):
        neibours = []
        node = None
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != j and abs(i) + abs(j) == 1:
                    node = Node(self.x + i, self.y + j)
                    if self.isReachable(node):
                        neibours.append(node)
        return neibours

    def isReachable(self, next):
        if self.distance(next) == 1 and (
                0 <= next.x < len(self.worldMap) and 0 <= next.y < len(self.worldMap[0]) and self.worldMap[next.x, next.y] == 0):
            return True
        else:
            return False

    def __setParent__(self, parent):
        self.parent = parent

    def __setCost__(self, cost):
        self.cost = cost

    def __hash__(self):
        return hash(self.x) * 1000 + hash(self.y)

    def __str__(self):
        return "(%s,%s)" % (self.x, self.y)

    @classmethod
    def setMap(clz, worldMap):
        clz.worldMap = worldMap

    @classmethod
    def setEnd(clz, end):
        clz.end = end

    @classmethod
    def setStart(clz, start):
        clz.start = start


# global openList
# global closeList
openDict = dict()
closeDict = dict()
linkedOpen = []


def astarMainLoop(startPoint, endPoint, worldMap):
    Node.setMap(worldMap)
    Node.setStart(Node(startPoint.x, startPoint.y))
    Node.setEnd(Node(endPoint.x, endPoint.y))
    # print(len(worldMap))
    # print(len(worldMap[0]))
    openDict[startPoint] = startPoint
    linkedOpen.append(startPoint)
    # openDict.openFDict
    while True:
        if openDict:
            # pick the minimal F
            curNode = linkedOpen.pop()
            if curNode.__eq__(endPoint):
                # return final path
                return curNode
            else:
                del openDict[curNode]
                closeDict[curNode] = curNode
                neibourNodeProcess(curNode)
        else:
            # unsuccesful
            return None


def neibourNodeProcess(curNode):
    neibours = curNode.fetchNeibours()
    for nnode in neibours:
        if not closeDict.has_key(nnode):
            if openDict.has_key(nnode):
                nnode = openDict.get(nnode)
                if nnode.parent is None:
                    print(nnode)
                if nnode.__selfCostFunction__() > curNode.__selfCostFunction__() + 1:
                    # 设置父节点
                    nnode.__setParent__(curNode)
                    nnode.__setCost__(curNode.cost + 1)
                else:
                    continue
            else:
                nnode.__setParent__(curNode)
                nnode.__setCost__(curNode.cost + 1)
                openDict[nnode] = nnode
                # 维护最小值 2分插入
                halfInsert(nnode, 0, len(linkedOpen) - 1)
                # print("insert")


# 折半插入
def halfInsert(node, start, end):
    if not linkedOpen:
        linkedOpen.append(node)
        return
    halfidx = (int)(math.floor((end - start) / 2) + start)
    val = linkedOpen[halfidx].__costFunction__()
    nval = node.__costFunction__()
    if end == start:
        if nval < val:
            linkedOpen.insert(end + 1, node)
        else:
            linkedOpen.insert(end, node)
        return
    if nval == val:
        linkedOpen.insert(halfidx, node)
        return
    if nval < val:
        halfInsert(node, halfidx + 1, end)
    else:
        halfInsert(node, start, halfidx)


def minF(endPoint):
    min = 9999
    minNode = None
    for node in openDict:
        cost = node.__costFunction__(endPoint)
        if cost < min:
            min = cost
            minNode = node
    return minNode


def init():
    global openDict, closeDict, linkedOpen
    openDict = dict()
    closeDict = dict()
    linkedOpen = []


if __name__ == "__main__":
    worldMap = np.zeros((50, 40))
    worldMap[35, 8:38] = 1
    worldMap[8:40, 5] = 1
    startPoint = Node(10, 30)
    endPoint = Node(46, 11)
    startPoint.__setCost__(0)
    node = astarMainLoop(startPoint, endPoint, worldMap)
    # print(str)

    print(node)
    if node is None:
        print("failure")
    else:
        curNode = node.parent
        while curNode.parent:
            print(curNode)
            curNode = curNode.parent

    print(startPoint)
