# 适用于大量危险天气存在时
# 基本思路是首先逃离危险天气区域，将区域划分为多个区域，当发现天气差时
# 寻路时避免靠近危险天气区域（可通过删除区域实现）

RESOLUTION = 20
THRE = 0.6


# 将区域划分
def departZone(maps, houridx):
    curMap = maps[houridx]
    xcnt = len(curMap) / RESOLUTION
    if len(curMap) % RESOLUTION > 0:
        xcnt += 1
    ycnt = len(curMap[0]) / RESOLUTION
    if len(curMap[0]) % RESOLUTION > 0:
        ycnt += 1
    zoneList = []
    for i in range(0, xcnt):
        if i == xcnt:
            for j in range(0, ycnt):
                zoneList.append(curMap[i * RESOLUTION:,
                                j * RESOLUTION:(j + 1) * RESOLUTION])
                if j == ycnt - 1:
                    zoneList.append(curMap[i * RESOLUTION:,
                                    j * RESOLUTION:])
        else:
            for j in range(0, ycnt):
                zoneList.append(curMap[i * RESOLUTION:(i + 1) * RESOLUTION,
                                j * RESOLUTION:(j + 1) * RESOLUTION])
                if j == ycnt - 1:
                    zoneList.append(curMap[i * RESOLUTION:(i + 1) * RESOLUTION,
                                    j * RESOLUTION:])
    return zoneList, curMap


def setDangerZone(curMap, zoneList):
    for zone in zoneList:
        if len(zone[zone > 1]) / len(zone) > THRE:
            zone[:, :] = 1
