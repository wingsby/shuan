# -*- coding: UTF-8 -*-
# 目标函数值 = 24*60*飞行器坠毁数 + 顺利到达的飞行器总飞行时长（分钟）

import time
import pandas as pd
import numpy as np

from astar import Tools
from astar.WeatherMapes import WeatherMapContainer
from astar.semifinal import Commons


def read_data(fname, head):
    """ read data """
    data = pd.read_csv(fname, iterator=True, header=head)
    loop = True
    chunksize = 10000000
    chunks = []
    while loop:
        try:
            chunk = data.get_chunk(chunksize)
            chunks.append(chunk)
        except StopIteration:
            loop = False
            print("Iteration is stopped.")
    df = pd.concat(chunks, ignore_index=True)
    return df


# class dataReader:
#     threshold = 15
#     mapes = dict()
#     hours = range(3, 21)
#     days = range(6, 11)  # to do change days
#     fileName = None
#
#     @classmethod
#     def setMapes(cls):
#         data = pd.read_csv(cls.fileName, iterator=True)
#         for day in cls.days:
#             for hour in cls.hours:
#                 cls.read(day, hour, data)
#         data.close()
#
#     @classmethod
#     def read(cls, day, hour, data):
#         chunkSize = 230708
#         try:
#             tmp = data.get_chunk(chunkSize)
#             cls.mapes[day * 100 + hour] = np.array(tmp['wind'].values).reshape(548, 421)
#         except StopIteration:
#             print("Iteration is stopped.")
#
#     def __init__(self, day, hour):
#         self.day = day
#         self.hour = hour
#         # self.weatherMap = np.zeros((548, 421))
#
#     def convertMap(self):
#         self.weatherMap[self.weatherMap < self.threshold] = 0
#         self.weatherMap[self.weatherMap >= self.threshold] = 1
#         return self.weatherMap
#
#     def getMap(self):
#         self.weatherMap = self.mapes[self.day * 100 + self.hour]
#         return self.convertMap()
#
#     def getMaps(self):
#         maps = []
#         for hour in range(3, 21):
#             map = self.mapes[self.day * 100 + hour]
#             map[map < self.threshold] = 0
#             map[map >= self.threshold] = 1
#             maps.append(map)
#         return maps


def is_crash(path, weather,date,target):
    """判断飞机是否坠毁"""
    for x, y, time in path.loc[:, ['xid', 'yid', 'time']].values:
        hour = int(time.split(':')[0])
        wind = weather[hour - 3][x - 1, y - 1]
        # rain=weather[hour-3][x-1,y-1]
        # wind=weather[weather['xid'].isin([x]) &
        #              weather['yid'].isin([y]) &
        #              weather['hour'].isin([hour])].wind.values

        if wind == 1:
            return True
    return False


################################################################
if __name__ == "__main__":

    # filePath="F:\\pywork\\shaun\\"
    filePath = "E:\\machineLearningData\\shaun\\test\\"
    # 存储
    start = time.time()
    days=range(6,11)

    # weather = read_data("F:\\pywork\\shaun\\input\\In_situMeasurementforTraining_201712.csv",0)
    # path = read_data(filePath+"output\\train\\v2_A_star_waitBadWeather15.csv",None)
    # score_file=open(filePath+"output\\train\\v2_A_star_waitBadWeather15_score.txt", "w+")
    # dataReader.fileName = "F:\\pywork\\shaun\\input\\ForecastDataforTesting_ensmean.csv"
    WeatherMapContainer.fileName = filePath + Commons.ensemblePath
    # dataReader.fileName = "F:\\pywork\\shaun\\input\\In_situMeasurementforTraining_201712.csv"
    WeatherMapContainer.days = days
    WeatherMapContainer.initWeatherMapes()

    path = read_data(filePath + "out.csv", None)
    score_file = open(filePath + "scores.txt", "w+")

    path.columns = ['target', 'date_id', 'time', 'xid', 'yid']
    ftime = 0
    crashNum = 0
    for date in days:  # 5
        # todo change date for input data (weather)
        oneMap = WeatherMapContainer.getWeatherMapes(date)
        # Tools.drawMap(oneMap[0])
        print()


        for tar in range(1, 11):  # 10
            # todo change date for output data (path)
            onepath = path[path['target'].isin([tar]) & path['date_id'].isin([date])]
            tmpTime = 2 * (len(onepath) - 1)
            if tmpTime < 0 or tmpTime > 18 * 60:  # 超时做坠毁处理
                ftime += 24 * 60
                crashNum += 1
            elif is_crash(onepath, oneMap,date,tar):
                ftime += 24 * 60
                crashNum += 1
            else:
                ftime += tmpTime
                score_file.write("target:%d; date_id:%d; fly_time: %d \n" % (tar, date, tmpTime))
                print("target:%d; date_id:%d; fly_time: %d" % (tar, date, tmpTime))

    print('===================')
    print('score: ', ftime)
    print('crashNum: ', crashNum)
    end = time.time()
    print("%f second" % (end - start))
    score_file.write('\nscore: %d\ncrashNum: %d\n%f second' % (ftime, crashNum, end - start))
    score_file.close()
