# coding:utf-8
# @Author: wangye
# @Description:
# @Date:Created  on 23:19 2018/2/5.
# @Modify
# ======================shaun=======================================
# -*- coding: utf-8 -*-
import copy
import matplotlib.pyplot as plt


def make_path(node):
    """根据节点绘制路径"""
    path = []
    while node:
        path.append((node.x, node.y))
        node = node.parent
    return path[::-1]

def make_nodepath(node):
    """根据节点绘制路径"""
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]


def mixedMaps(node, range, maps):
    idx = node.cost / 30
    zone = findCloseZone(node, range, maps[idx])
    mixMap = maps[idx + 1]
    for [x, y] in zone:
        mixMap[x, y] = (maps[idx])[x, y]
    return mixMap

# 最近的步数采用当前时间,往前再多看一个小时，然后终点前都为无障碍
def endValidMixedMaps(node, maps, stime):
    minute = node.cost % 30 * 2 + stime % 100
    hour = node.cost / 30 + stime / 100
    if minute >= 60:
        minute -= 60
        hour += 1
    idx=hour-3
    range=(60-minute)/2
    mixMap = copy.copy(maps[idx])
    mixMap[:, :] = 0
    if idx+1<len(maps):
        zone = findCloseZone(node, range+30, maps[idx+1])
        for [x, y] in zone:
            mixMap[x, y] = (maps[idx+1])[x, y]
    zone1 = findCloseZone(node, range, maps[idx])
    for [x, y] in zone1:
        mixMap[x, y] = (maps[idx])[x, y]
    return mixMap

#寻找Manhattan距离为range的区域
def findCloseZone(node, steps, map):
    if node.x >= 0:
        x0 = node.x - steps
    else:
        x0 = 0
    if node.x >= len(map) - steps:
        x1 = len(map)-1
    else:
        x1 = node.x + steps

    if node.y >= 0:
        y0 = node.y - steps
    else:
        y0 = 0
    if node.y >= len(map[0]) - steps:
        y1 = len(map[0])-1
    else:
        y1 = node.y + steps

    zone = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if ManhattanDistance(x, y, node.x, node.y) <= steps:
                zone.append([x, y])
    return zone


def ManhattanDistance(x0, y0, x1, y1):
    dis = abs(x0 - x1) + abs(y0 - y1)
    return dis


def drawRoute(worldMap,node,startPoint):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(worldMap)
    plt.scatter(node.y, node.x, marker='X')
    if node is None:
        print("failure")
    else:
        curNode = node.parent
        while curNode.parent:
            plt.scatter(curNode.y, curNode.x, s=5)
            curNode = curNode.parent

    plt.scatter(startPoint.y, startPoint.x, marker='s')
    plt.show()

def drawMap(worldMap):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(worldMap)
    # plt.scatter(node.y, node.x, marker='X')
    # if node is None:
    #     print("failure")
    # else:
    #     curNode = node.parent
    #     while curNode.parent:
    #         plt.scatter(curNode.y, curNode.x, s=5)
    #         curNode = curNode.parent
    #
    # plt.scatter(startPoint.y, startPoint.x, marker='s')
    plt.show()

