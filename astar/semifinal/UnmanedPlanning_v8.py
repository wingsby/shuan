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

import time

import numpy as np
import pandas as pd
import astar.Tools as Tools
from astar.BackRestartModel import BackRestartModel
from astar.semifinal import TimePickStrategy, Commons

sys.path.append(os.path.abspath("F\\pywork\\astar"))
from astar import WeatherMapReader, HashAstar
from astar.LocalOptimalModel import LocalOptimalModel


# ==================================================================
# 每一架飞机的路径
def oneSub(path, target, date_id, stime):
    """ create one submit path """
    sub_df = pd.DataFrame(columns=['target', 'date_id', 'time', 'xid', 'yid'])
    try:
        length = len(path)
        # 存储路径
        sub_df['xid'] = path[:, 0]
        sub_df['yid'] = path[:, 1]
        sub_df.xid = sub_df.xid.astype(np.int32)  # df.astype 对df进行数据格式转换，支持python和numpy的数据类型
        sub_df.yid = sub_df.yid.astype(np.int32)
        sub_df.target = target
        sub_df.date_id = date_id
        #### add time
        hour = stime / 100
        minute = stime % 100
        ti = datetime(2017, 11, 21, hour, minute)
        tm = [ti.strftime('%H:%M')]
        for i in range(length - 1):
            ti = ti + timedelta(minutes=2)
            tm.append(ti.strftime('%H:%M'))
        sub_df.time = tm
    except TypeError:
        print('==== Path no found for date %d, target %d ====' % (date_id, target))
    return sub_df


def changeRegionMap(sx, sy, ex, ey, daymaps, changehour):
    """改变起点周围30步内的map"""
    newMap = np.zeros((548, 421))
    for hour in range(17, changehour - 1, -1):
        hourId = hour - changehour
        x1 = max(sx - 30 * (hourId + 1), 0)
        x2 = min(sx + 30 * (hourId + 1), 547)
        y1 = max(sy - 30 * (hourId + 1), 0)
        y2 = min(sy + 30 * (hourId + 1), 420)
        newMap[x1:x2, y1:y2] = daymaps[hour][x1:x2, y1:y2]
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.imshow(newMap)
    # plt.scatter(sy,sx,  marker='s')
    # plt.scatter(ey, ex, marker='X')
    return newMap


# 无障碍
def PathPlaning(sx, sy, ex, ey, daymaps, successMap, failedMap, day, target, smap, emap):
    path = []
    startPoint = HashAstar.Node(sx, sy)
    endPoint = HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)
    # first try A STAR
    HashAstar.init()
    firstMap = np.zeros((548, 421))
    node = HashAstar.astarMainLoop(startPoint, endPoint, firstMap)
    shour = smap.get(day)
    sminute = 0
    stime = (shour + 3) * 100 + sminute
    failNodes, flag = collectFailNodes(node, shour, sminute, daymaps)
    fmap = dict()
    if flag:
        # node 必为end
        if node in successMap:
            successMap[node].append(stime)
        else:
            successMap[node] = [stime]
    else:
        if failNodes:
            fmap[stime] = failNodes
    etimes = emap.get(day * 100 + target)
    if not etimes:
        return False
    while stime <= 2100:
        sminute += 10
        if sminute >= 60:
            sminute -= 60
            shour += 1
        stime = (shour + 3) * 100 + sminute
        for etime in etimes:
            if etime * 60 - shour * 60 - sminute >= endPoint.distance(startPoint) * 2 \
                    >= (etime - 1) * 60 - shour * 60 - sminute:
                failNodes, flag = collectFailNodes(node, shour, sminute, daymaps)
                if flag:
                    # node 必为end
                    if node in successMap:
                        successMap[node].append(stime)
                    else:
                        successMap[node] = [stime]
                else:
                    if failNodes:
                        fmap[stime] = failNodes
    failedMap[target] = fmap
    return True

# 检测错误节点并记录下来
def collectFailNodes(node, shour, sminute, daymaps):
    path = Tools.make_path(node)
    index = 0
    nodelist = []
    while index < len(path):
        xid, yid = path[index][0], path[index][1]
        hour = 3 + int(index / 30) + shour
        minute = index % 30 + sminute
        if minute >= 60:
            hour += 1
            minute -= 60
        if hour > 20:
            # 超时
            return None, False
        if daymaps[hour - 3][xid, yid] > 0:
            nodelist.append(path[index])
        index += 1
    if len(nodelist) > 0:
        return nodelist, True
    else:
        return nodelist, False


def failNodeRePlan(sx,sy,ex,ey,fmap,target,daymaps):
    # pick current etime is valid or currentMap is valid
    cost=abs(sx-ex)+abs(sy-ey)*2
    for stime in fmap:
        addhour= np.math.ceil((cost + stime % 100) / 60.)
        ehour= stime/100*100+addhour
        if (daymaps[ehour])[ex-1][ey-1]==0 and (daymaps[ehour+1])[ex-1][ey-1]==0:
            # first 序列
            node=failNodePathPlaning



def failNodePathPlaning(sx, sy, ex, ey, target, day, daymaps,stime):
    path = []
    startPoint = HashAstar.Node(sx, sy)
    endPoint = HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)
    # first try A STAR
    HashAstar.init()
    shour=stime/100
    sminute=stime%100
    #问题在于起始点结束点有可能没有通路
    node = HashAstar.astarMainLoop(startPoint, endPoint, daymaps[shour-3])

    # check nodes until break;
    failNode = checkFailNodes(node)
    # try backresatart
    brm_node = failNode
    while not brm_node:
        failNode = checkFailNodes(brm_node)
        HashAstar.init()
        brm = BackRestartModel(failNode, endPoint, daymaps)
        brm_node = brm.doBackAndPlan()
        if brm_node.__eq__(endPoint):
            return brm_node

def checkFailNodes(node, shour, sminute):
    path = Tools.make_path(node)
    index = 0
    while index < len(path):
        xid, yid = path[index][0], path[index][1]
        hour = 3 + int(index / 30) + shour
        minute = index % 30 + sminute
        if minute >= 60:
            hour += 1
            minute -= 60
        if hour > 20:
            break
        if daymaps[hour - 3][xid, yid] == 1:
            return path[index]
        index += 1



# =================================================================================================

if __name__ == "__main__":
    start = time.time()
    # filePath = "K:\\pywork\\shaun\\"
    # filePath = "I:\\python work\\shuan\\pancy\\"
    # filePath = "E:\\machineLearningData\\shaun\\"
    filePath = Commons.filePath
    # filePath = "F:\\ml\\data\\"
    # city = pd.read_csv(filePath + "input\\CityData.csv")
    city = pd.read_csv(filePath + "CityData.csv")
    city_array = city.values - 1
    days = Commons.days

    # 读取weather map
    WeatherMapReader.WeatherMapReader.fileName = filePath + Commons.subPath + Commons.ensemblePath;
    # WeatherMapReader.WeatherMapReader.fileName = filePath + "input\\ForecastDataforTesting_ensmean.csv"
    # WeatherMapReader.WeatherMapReader.days = range(6, 11)
    WeatherMapReader.WeatherMapReader.days = days
    WeatherMapReader.WeatherMapReader.threshold = 14
    WeatherMapReader.WeatherMapReader.setMapes()
    middle = time.time()
    print("time for read data: %f second" % (middle - start))

    # save data
    sub_csv = pd.DataFrame(columns=['target', 'date_id', 'time', 'xid', 'yid'])
    # for day in range(6, 11):
    for day in days:
        reader = WeatherMapReader.WeatherMapReader(day, 3)
        daymaps = reader.getMaps()
        stimeMap = dict()
        # 各站时间的最优策略
        # timeMap = TimePickStrategy.decideTimePickStrategy(daymaps)
        for target in range(1, 11):
            # stime = timeMap.get(target)
            node, stime = PathPlaning(int(city_array[0][1]), int(city_array[0][2]), \
                                      int(city_array[target][1]), int(city_array[target][2]), \
                                      daymaps, stimeMap)

            # start two
            if node:
                onepath = Tools.make_path(node)
                sub_df = oneSub(np.array(onepath) + 1, target, day, stime)
                # wname = ("%s\\output\\out_%d_%d.csv" % (filePath, day, target))
                sub_csv = pd.concat([sub_csv, sub_df], axis=0)
            else:
                print("wrong on %d !" % target)

    # 输出数据
    wname = ("%s\\%s\\%s" % (filePath, Commons.subPath, Commons.outPutPath))
    sub_csv.target = sub_csv.target.astype(np.int32)
    sub_csv.date_id = sub_csv.date_id.astype(np.int32)
    sub_csv.xid = sub_csv.xid.astype(np.int32)
    sub_csv.yid = sub_csv.yid.astype(np.int32)
    sub_csv.to_csv(wname, header=False, index=False)
    end = time.time()
    print("time for A-star: %f second" % (end - middle))