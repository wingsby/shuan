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
from astar.HashAstar import Node
from astar.semifinal import TimePickStrategy, Commons, ValidTime

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


# 无障碍
# @successMap: 成功的节点 结构 key：day value：dict（key ：target value:[(node,stime)])
# @failedMap:失败的节点 key:day*100+target value: dict(key:stime value: nodelist)
# @smap：起始时间表 key: day value:最早有效hour
# @emap: 结束时间表 key:day*100+target value: [etime]
# 返回： false：etime不存在    true：程序运行结束，无其他意思
def PathPlaning(sx, sy, ex, ey, daymaps, successMap, failedMap, day, cityid, smap, emap):
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
    stime = shour * 100 + sminute
    failNodes, flag = collectFailNodes(node, shour, sminute, daymaps)
    if day * 100 + cityid in failedMap:
        fmap = failedMap.get(day * 100 + cityid)
    else:
        fmap = dict()
    if day in successMap:
        sumap = successMap.get(day)
    else:
        sumap = dict()
    if flag:
        # node 必为end
        if cityid in sumap:
            sumap[cityid].append((node, stime))
        else:
            sumap[cityid] = [(node, stime)]
    else:
        if failNodes:
            fmap[stime] = failNodes
    etimes = emap.get(day * 100 + cityid)
    if not etimes:
        return False
    while stime <= 2100:
        sminute += 10
        if sminute >= 60:
            sminute -= 60
            shour += 1
        stime = shour * 100 + sminute
        # etime 其实是ehour
        for etime in etimes:
            if etime * 60 - shour * 60 - sminute >= endPoint.distance(startPoint) * 2 \
                    >= (etime - 1) * 60 - shour * 60 - sminute:
                failNodes, flag = collectFailNodes(node, shour, sminute, daymaps)
                if flag:
                    # node 必为end
                    if cityid in sumap:
                        sumap[cityid].append((node, stime))
                    else:
                        sumap[cityid] = [(node, stime)]
                else:
                    if failNodes:
                        fmap[stime] = failNodes
    failedMap[day * 100 + cityid] = fmap
    successMap[day] = sumap
    return True


# 检测错误节点并记录下来,返回True时意味着成功
# 返回说明： FALSE 寻路失败，True寻路成功
#           None 无节点返回（超时或成功）
def collectFailNodes(node, shour, sminute, daymaps):
    path = Tools.make_path(node)
    index = 0
    nodelist = []
    while index < len(path):
        xid, yid = path[index][0], path[index][1]
        hour = int(index / 30) + shour
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
        return nodelist, False
    else:
        return None, True


def failNodeRePlan(sx, sy, ex, ey, fmap, target, daymaps, successMap):
    # pick current etime is valid or currentMap is valid
    if day in successMap:
        sumap = successMap.get(day)
    else:
        sumap = dict()
    cost = (abs(sx - ex) + abs(sy - ey)) * 2
    for stime in fmap:
        addhour = int(np.math.ceil((cost + stime % 100) / 60.))
        ehour = stime / 100 + addhour
        if ehour >= 21:
            continue
        if (daymaps[ehour - 3])[ex - 1][ey - 1] == 0:
            # first 序列
            node = failNodePathPlaning(sx, sy, ex, ey, target, day, daymaps, stime)
            if node:
                if target in sumap:
                    sumap[target].append((node, stime))
                else:
                    sumap[target] = [(node, stime)]
    successMap[day] = sumap


def failNodePathPlaning(sx, sy, ex, ey, target, day, daymaps, stime):
    path = []
    startPoint = HashAstar.Node(sx, sy)
    endPoint = HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)
    # first try A STAR
    HashAstar.init()
    # 问题在于起始点结束点有可能没有通路
    # 假设最近小时步数为这一小时，下一小时步数为下一小时，其他区域为通路
    noWeather = np.zeros((548, 421))
    tnode = HashAstar.astarMainLoop(startPoint, endPoint, noWeather)
    # check nodes until break;
    failNode, flag = checkFailNodes(tnode, stime / 100, stime % 100)
    if flag:
        return tnode
    # try backresatart
    brm_node = failNode
    while brm_node:
        HashAstar.init()
        # Tools.endValidMixedMaps()
        brm = BackRestartModel(Node(failNode[0],failNode[1]), endPoint, daymaps, stime)
        brm_node = brm.doBackAndPlan()
        if brm_node.__eq__(endPoint):
            return brm_node
        failNode = checkFailNodes(brm_node)


def checkFailNodes(node, shour, sminute):
    path = Tools.make_path(node)
    index = 0
    while index < len(path):
        xid, yid = path[index][0], path[index][1]
        hour = int(index / 30) + shour
        minute = index % 30 + sminute
        if minute >= 60:
            hour += 1
            minute -= 60
        if hour > 20:
            return None, False
        if daymaps[hour - 3][xid, yid] == 1:
            return path[index], False
        index += 1
    return None, True


# =================================================================================================

if __name__ == "__main__":
    start = time.time()
    # filePath = "E:\\machineLearningData\\shaun\\"
    filePath = Commons.filePath
    city = pd.read_csv(filePath + "CityData.csv")
    city_array = city.values - 1
    days = Commons.days
    # 读取weather map
    WeatherMapReader.WeatherMapReader.fileName = filePath + Commons.subPath + Commons.ensemblePath;
    # WeatherMapReader.WeatherMapReader.fileName = filePath + "input\\ForecastDataforTesting_ensmean.csv"
    WeatherMapReader.WeatherMapReader.days = days
    WeatherMapReader.WeatherMapReader.threshold = 14
    WeatherMapReader.WeatherMapReader.setMapes()
    middle = time.time()
    print("time for read data: %f second" % (middle - start))
    # save data
    sub_csv = pd.DataFrame(columns=['target', 'date_id', 'time', 'xid', 'yid'])

    stimeMap, etimeMap = ValidTime.getTime()
    successMap = dict()
    failMap = dict()
    for target in range(1, 11):
        for day in days:
            reader = WeatherMapReader.WeatherMapReader(day, 3)
            daymaps = reader.getMaps()
            # 各站时间的最优策略
            # timeMap = TimePickStrategy.decideTimePickStrategy(daymaps)
            flag = PathPlaning(int(city_array[0][1]), int(city_array[0][2]), \
                               int(city_array[target][1]), int(city_array[target][2]), \
                               daymaps, successMap, failMap, day, target, stimeMap, etimeMap)
            #     print()
            # print()

    # key=100*day+target
    for key in failMap:
        fmap = failMap.get(key)
        target = key % 100
        if len(fmap) > 0:
            failNodeRePlan(int(city_array[0][1]), int(city_array[0][2]), int(city_array[target][1]),
                           int(city_array[target][2]), fmap, target, daymaps, successMap)

    # 分配各日时间安排，同一日优先时间长的，同一城市优先步数少的
    # skey=day
    # 每日安排，只有一个
    finalMap = dict()
    for skey in successMap:
        sumap = successMap.get(skey)
        dayFinal = dict()
        # todo 按长度排序
        for target in Commons.cityorder:
            if target in sumap:
                tmplist = sumap[target]
            else:
                tmplist = []
            minlen = 9999
            mintime = 9999;
            minnode = None
            tnode = None
            ttime = None
            ttarget = None
            node = None
            for (node, stime) in tmplist:
                continueFlag = False
                for (tnode, ttime, ttarget) in dayFinal.values():
                    if ttime == stime:
                        continueFlag = True
                        break
                if continueFlag:
                    continue
                # 首先选择时间，通常选最早的
                if minlen > node.cost:
                    minlen = node.cost
                    mintime = stime
                    minnode = node
                else:
                    if minlen == node.cost:
                        if stime < mintime:
                            minlen = node.cost
                            mintime = stime
                            minnode = node
            if mintime < 9999:
                dayFinal[target] = (minnode, mintime, target)
            else:
                # 有错的只赋值一格
                wrong = 1920
                for (tnode, ttime, ttarget) in dayFinal.values():
                    if wrong == ttime:
                        wrong += 10
                dayFinal[target] = (Node(int(city_array[target][1]), int(city_array[target][2])), wrong, target)
        finalMap[skey] = dayFinal

    # # 写文件
    for target in range(1, 11):
        for day in days:
            dayFinal = finalMap.get(day)
            if not dayFinal:
                continue
            (node, stime, target) = dayFinal.get(target)
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
