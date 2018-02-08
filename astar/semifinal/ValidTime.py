# coding:utf-8
# @Author: wangye
# @Description:
# @Date:Created  on 23:19 2018/2/7.
# @Modify
# ======================shaun=======================================
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from astar import WeatherMapes
from astar.HashAstar import Node
from astar.semifinal import Commons

# 其中只计算有可能的有效点
endValidMap = dict()
startValidMap = dict()
def init():
    # key targe_day: [hour]
    filePath = Commons.filePath
    city = pd.read_csv(filePath + "CityData.csv")
    city_array = city.values - 1
    WeatherMapes.WeatherMapContainer.days = Commons.days
    WeatherMapes.WeatherMapContainer.threshold = 14
    WeatherMapes.WeatherMapContainer.initWeatherMapes()
    startPoint = Node(city_array[0][1], city_array[0][2])

    for day in Commons.days:
        daymaps = WeatherMapes.WeatherMapContainer.getWeatherMapes(day)
        # start
        for hour in range(3, 21):
            if (daymaps[hour - 3])[startPoint.x - 1][startPoint.y - 1] < 1:
                if day in startValidMap:
                    continue
                else:
                    startValidMap[day] = hour
        # end
        for hour in range(3, 21):
            for target in range(1, 11):
                endPoint = Node(city_array[target][1], city_array[target][2])
                costHour = np.math.ceil(endPoint.distance(startPoint) * 2 / 60)
                if hour - startValidMap.get(day) >= costHour and (daymaps[hour - 3])[endPoint.x - 1][
                            endPoint.y - 1] < 1:
                    if day * 100 + target in endValidMap:
                        endValidMap[day * 100 + target].append(hour)
                    else:
                        endValidMap[day * 100 + target] = [hour]


def getTime():
    if len(startValidMap) < 1:
        init()
    return startValidMap, endValidMap
