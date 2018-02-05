# coding:utf-8
# @Author: wangye
# @Description:
# @Date:Created  on 10:31 2018/1/28.
# @Modify
# ======================shaun=======================================
import sys
import time

from astar import HashAstar

sys.path.append("C:\Python27\Lib\site-packages")
import numpy as np
import matplotlib.pyplot as plt



if __name__ == '__main__':
        # plt.bar(left=0, height=1)
        worldMap = np.zeros((1000, 1000))
        worldMap[35, 8:] = 1
        worldMap[8:, 5] = 1
        worldMap[135, 3:] = 1
        startPoint = HashAstar.Node(10, 930)
        endPoint =  HashAstar.Node(846, 11)
        startPoint.__setCost__(0)
        start=time.time()
        node = HashAstar.astarMainLoop(startPoint, endPoint, worldMap)
        print("耗时：%d 秒" %(time.time()-start))
        #绘图
        fig = plt.figure()
        ax = fig.add_subplot(221)
        ax.imshow(worldMap)
        plt.scatter(node.y,node.x,marker='X')
        if node is None:
            print("failure")
        else:
            curNode = node.parent
            while curNode.parent:
                plt.scatter(curNode.y, curNode.x,s=5)
                curNode = curNode.parent

        plt.scatter(startPoint.y, startPoint.x,marker='s')
        plt.show()


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


