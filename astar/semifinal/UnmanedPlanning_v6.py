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
import Tools

from astar.BackRestartModel import BackRestartModel

sys.path.append(os.path.abspath("F\\pywork\\astar"))
from astar import WeatherMapReader, HashAstar
from astar.LocalOptimalModel import LocalOptimalModel


# ==================================================================
# 每一架飞机的路径
def oneSub(path, target, date_id):
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
        ti = datetime(2017, 11, 21, 3, 0)
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


def PathPlaning(sx, sy, ex, ey, target, day, daymaps):
    path = []
    startPoint = HashAstar.Node(sx, sy)
    endPoint = HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)
    # first try A STAR
    HashAstar.init()
    node = HashAstar.astarMainLoop(startPoint, endPoint, daymaps[0])
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
            # brm_node为None，说明无法完成搜索，此时天气条件较为恶劣
            # 应可采用局部最优模型，考虑2个时次
            # todo tomorrow
            # LocalOptimalModel()





            # 失败节点


def checkFailNodes(node):
    path = Tools.make_path(node)
    index = 0
    while index < len(path):
        xid, yid = path[index][0], path[index][1]
        hour = 3 + int(index / 30)
        minute = index % 30
        if hour > 20:
            break
        if daymaps[hour - 3][xid, yid] == 1:
            return path[index]
        index += 1


def findPath(sx, sy, ex, ey, target, day, daymaps, backStep):
    """生成A-STAR 路径"""
    path = []
    startPoint = HashAstar.Node(sx, sy)
    endPoint = HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)
    now = HashAstar.Node(startPoint.x, startPoint.y)
    now.__setCost__(0)
    for houridx in range(0, 18):
        model = LocalOptimalModel()
        node = model.doFindPath(houridx, now, endPoint, daymaps)
        if not node:
            return None
        new_path = Tools.make_path(node)
        path = path + new_path
        if node.__eq__(endPoint):
            return path
        now = HashAstar.Node(node.x, node.y)
        now.__setCost__(0)


# =================================================================================================

if __name__ == "__main__":
    start = time.time()
    # filePath = "K:\\pywork\\shaun\\"
    # filePath = "I:\\python work\\shuan\\pancy\\"
    filePath = "E:\\machineLearningData\\shaun\\"
    # city = pd.read_csv(filePath + "input\\CityData.csv")
    city = pd.read_csv(filePath + "CityData.csv")
    city_array = city.values - 1

    # 读取weather map
    WeatherMapReader.WeatherMapReader.fileName = filePath + "ForecastDataforTesting_ensmean.csv"
    # WeatherMapReader.WeatherMapReader.fileName = filePath + "input\\ForecastDataforTesting_ensmean.csv"
    WeatherMapReader.WeatherMapReader.days = range(6, 11)
    WeatherMapReader.WeatherMapReader.threshold = 15
    WeatherMapReader.WeatherMapReader.setMapes()
    backStep = 2

    middle = time.time()
    print("time for read data: %f second" % (middle - start))

    # save data
    sub_csv = pd.DataFrame(columns=['target', 'date_id', 'time', 'xid', 'yid'])
    for day in [6]:  # range(6,11):
        reader = WeatherMapReader.WeatherMapReader(day, 3)
        daymaps = reader.getMaps()
        for target in [4]:  # range(1,11):
            onepath = findPath(city_array[0][1], city_array[0][2], \
                               city_array[target][1], city_array[target][2], \
                               target, day, daymaps, backStep)
            sub_df = oneSub(onepath, target, day)
            sub_csv = pd.concat([sub_csv, sub_df], axis=0)
    sub_csv.target = sub_csv.target.astype(np.int32)
    sub_csv.date_id = sub_csv.date_id.astype(np.int32)
    sub_csv.xid = sub_csv.xid.astype(np.int32)
    sub_csv.yid = sub_csv.yid.astype(np.int32)
    # sub_csv.to_csv(filePath+"output\\test_with_everyhour_weather_regionIn30Step_back2.csv",header=False,index=False)

    end = time.time()
    print("time for A-star: %f second" % (end - middle))
