#astar
#5

safeThreshold=0.4
import math

def chooseSafeRegion(maps,hourIdx,start,end):
    #获取当前点区域范围
    pass



def safeRegionDefined(maps,hourIdx,start):
    curMap=maps[hourIdx]
    nextMap=maps[hourIdx+1]
    #distance 为30步的范围
    if start.x>=30:
        x0=start.x-30
    else:
        x0=0
    if start.x>len(curMap[0]-30):
        x1=len(curMap[0])
    else:
        x1=start.x-30



    cur1=len(curMap[curMap>1])
    next1=len(nextMap[nextMap>1])
