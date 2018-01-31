# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import *
import time
import sys,os
sys.path.append(os.path.abspath("F\\pywork\\astar"))
import astar.HashAstar, astar.WeatherMapReader, astar.plottest


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

def make_path(node):
    """根据节点绘制路径"""
    path=[]
    while node:
        path.append((node.x,node.y))
        node=node.parent
    return path[::-1]

def changeRegionMap(new_sx,new_sy,daymap,predaymap):
    """改变起点周围30步内的map"""
    newMap=np.zeros((548, 421))
    x1=max(new_sx-30,0)
    x2=min(new_sx+30,547)
    y1=max(new_sy-30,0)
    y2=min(new_sy+30,420)
    newMap[x1:x2,y1:y2]=daymap[x1:x2,y1:y2]+predaymap[x1:x2,y1:y2]
    newMap[newMap==2]=1
    return newMap

def findPath(sx,sy,ex,ey,target, day, daymaps, backStep):
    """生成A-STAR 路径"""
    startPoint = astar.HashAstar.Node(sx, sy)
    endPoint = astar.HashAstar.Node(ex, ey)
    startPoint.__setCost__(0)

    # A-star寻路
    worldMap = np.zeros((548, 421))
    astar.HashAstar.init()
    node = astar.HashAstar.astarMainLoop(startPoint, endPoint, worldMap)
    path=make_path(node)

    # 对第一次得到的best-path进行检测，如果有碰到bad-weather，那么记录该点为新的start，
    # end为原来的end
    # 根据新的start和end重新寻路（这时候用start所在时次的障碍）
    # 把新的路径替换原来的路径
    index=0
    while index<len(path):
        xid,yid=path[index][0],path[index][1]
        hour = 3+int(index /30)
        minute = index % 30
        if hour>20:
            break
        if daymaps[hour-3][xid,yid] == 1:
            if index == 0: # todo 在起点就遇到坏天气怎么处理？
                return []
            elif minute >0: # 如果是在1个小时内退backStep步躲避
                new_sx, new_sy = path[index - backStep][0], path[index - backStep][1]
                startPoint = astar.HashAstar.Node(new_sx, new_sy)
                endPoint = astar.HashAstar.Node(ex, ey)
                startPoint.__setCost__(0)
                # A-star寻路
                astar.HashAstar.init()
                node = astar.HashAstar.astarMainLoop(startPoint, endPoint, changeRegionMap(new_sx, new_sy, daymaps[hour - 3], daymaps[hour - 3])) # daymaps[hour-3]
                new_path = make_path(node)
                if not new_path:
                    return new_path
                path = path[0:index - backStep] + new_path
                index = index - backStep
            else: # 如果在天气交接时刻，有可能出现调整后周围全是坏天气，那么退后30步，同时用两个时次的weather
                new_sx, new_sy = path[index - 30][0], path[index - 30][1]
                startPoint = astar.HashAstar.Node(new_sx, new_sy)
                endPoint = astar.HashAstar.Node(ex, ey)
                startPoint.__setCost__(0)
                # A-star寻路
                astar.HashAstar.init()
                todaymap=changeRegionMap(new_sx,new_sy,daymaps[hour-3],daymaps[hour-3])
                yestadaymap=changeRegionMap(new_sx,new_sy,daymaps[hour-3-1],daymaps[hour-3-1])
                node = astar.HashAstar.astarMainLoop(startPoint, endPoint, changeRegionMap(new_sx, new_sy, daymaps[hour - 3], daymaps[hour - 3 - 1])) # daymaps[hour-3]
                new_path = make_path(node)
                if not new_path:
                    return new_path
                path = path[0:index - 30] + new_path
                index = index - 30

        index += 1
    return np.array(path)+1



# =================================================================================================

if __name__ == "__main__":
    start=time.time()
    filePath="K:\\pywork\\shaun\\"
    city = pd.read_csv(filePath + "input\\CityData.csv")
    city_array=city.values-1

    # 读取weather map
    astar.WeatherMapReader.WeatherMapReader.fileName = filePath + "input\\ForecastDataforTesting_ensmean.csv"
    astar.WeatherMapReader.WeatherMapReader.days = range(6, 11)
    astar.WeatherMapReader.WeatherMapReader.threshold = 15
    astar.WeatherMapReader.WeatherMapReader.setMapes()
    backStep = 2

    middle = time.time()
    print("time for read data: %f second" % (middle - start))

    # save data
    sub_csv = pd.DataFrame(columns=['target','date_id','time','xid','yid'])
    for day in [6]:#range(6,11):
        reader = astar.WeatherMapReader.WeatherMapReader(day, 3)
        daymaps = reader.getMaps()
        for target in [4]:#range(1,11):
            onepath = findPath(city_array[0][1], city_array[0][2], \
                                city_array[target][1], city_array[target][2], \
                                target, day, daymaps,backStep)
            sub_df = oneSub(onepath, target, day)
            sub_csv = pd.concat([sub_csv, sub_df], axis=0)
    sub_csv.target = sub_csv.target.astype(np.int32)
    sub_csv.date_id = sub_csv.date_id.astype(np.int32)
    sub_csv.xid = sub_csv.xid.astype(np.int32)
    sub_csv.yid = sub_csv.yid.astype(np.int32)
    # sub_csv.to_csv(filePath+"output\\test_with_everyhour_weather_regionIn30Step_back2.csv",header=False,index=False)

    end = time.time()
    print("time for A-star: %f second" % (end - middle))
