# -*- coding: utf-8 -*-
# @Author: wangye
# @Description:
# @Date:Created  on 23:27 2018/1/27.
# @Modify
#
import numpy as np


class Node:
    __hash__ = object.__hash__
    worldMap = []

    def __init__(self, xi, yi):
        self.x = xi
        self.y = yi
        self.parent = None
        # g cost
        self.cost = -1

    # G 当前代价
    def __selfCostFunction__(self):
        if self.cost >= 0:
            return self.cost
        else:
            self.cost = self.parent.cost + 1
            return self.parent.cost + 1

    # 曼哈顿距离
    def distance(self, next):
        return abs(next.x - self.x) + abs(next.y - self.y)

    # F = G + H 估计代价未知
    def __costFunction__(self, end):
        g = self.__selfCostFunction__()
        h = self.distance(end)
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
                0 <= next.x < len(self.worldMap) and 0 <= next.y < len(self.worldMap) and self.worldMap[
            next.x, next.y]) == 0:
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


# global openList
# global closeList
openDict = []
closeList = []


def astarMainLoop(startPoint, endPoint, worldMap):
    Node.setMap(worldMap)
    print(len(worldMap))
    print(len(worldMap[0]))
    openDict.append(startPoint)
    while (True):
        # if len(openList) % 10 == 0:
        #     print("open: %s" % len(openList))
        #     print("close: %s" % len(closeList))
        if openDict:
            # pick the minimal F
            curNode, min = minimalFofOpenList(endPoint)
            if curNode.__eq__(endPoint):
                # return final path
                return curNode
            else:
                openDict.remove(curNode)
                closeList.append(curNode)
                neibourNodeProcess(curNode)
                # print("check openlist")
        else:
            # unsuccesful
            return None


def neibourNodeProcess(curNode):
    neibours = curNode.fetchNeibours()
    # in neibours not in closeList
    neiboursDifClose = list(set(neibours).difference(set(closeList)))
    global openDict
    # in neibours not in openlist
    neiboursUnionOpen = list(set(neiboursDifClose).union(set(openList)))
    openList = neiboursUnionOpen
    for node in openList:
        if node.parent is None:
            node.__setParent__(curNode)
            node.__setCost__(curNode.cost + 1)
    # in neibours  in openlist
    neiboursInternOpen = list(set(neiboursDifClose).intersection(set(openList)))
    for node in neiboursInternOpen:
        if node.__selfCostFunction__() > curNode.__selfCostFunction__() + 1:
            # 设置父节点
            node.__setParent__(curNode)


# def neibourNodeProcess(curNode):
#     neibours = curNode.fetchNeibours()
#     for nnode in neibours:
#         cflag,nnode= isInList(nnode, closeList)
#         if not cflag:
#             oflag,nnode= isInList(nnode, openList)
#             if oflag:
#                 if nnode.cost <= 0:
#                     print(nnode)
#                 if nnode.__selfCostFunction__() > curNode.__selfCostFunction__() + 1:
#                     # 设置父节点
#                     nnode.__setParent__(curNode)
#                     nnode.__setCost__(curNode.cost + 1)
#                 else:
#                     continue
#             else:
#                 nnode.__setParent__(curNode)
#                 nnode.__setCost__(curNode.cost + 1)
#                 openList.append(nnode)


# def isInList(node, alist):
#     tmp=[node]
#     cnode=list(set(tmp).intersection(set(alist)))
#     if not cnode :
#         return False,node
#     else:
#         if(cnode[0].parent is None):
#             print(cnode)
#         return True,cnode
#     # for tnode in list:
#     #     if tnode.__eq__(node):
#     #         return True, tnode
#     # return False, node


def minimalFofOpenList(endPoint):
    min = 9999
    minNode = None
    for node in openDict:
        cost = node.__costFunction__(endPoint)
        if cost < min:
            min = cost
            minNode = node
    return minNode, min


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
