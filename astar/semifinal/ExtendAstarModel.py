from astar import Tools

#1. 寻路只寻路
class ExtendAstarModel:
    # 乐观算法，强调绝不走回头路，每一步都向目标前进
    #扩散法一旦发现寻路失败
    __stime = 0
    def __init__(self, curNode, endPoint, maps, stime):
        self.curNode = curNode
        self.endPoint = endPoint
        self.maps = maps
        self.path = Tools.make_nodepath(self.curNode)
        self.stime = stime

    # 在较为极端的情况下无法完成寻路任务
    def doBackAndPlan(self):
        minute = self.curNode.cost % 30 * 2 + self.stime % 100
        hour = self.curNode.cost / 30 + self.stime / 100
        if minute >= 60:
            minute -= 60
            hour += 1
        #当前小时
        backstep = minute / 2
        restart = self.path[self.curNode.cost - backstep]
        # 当切换时次时出错，此时应该如何？
        # 可以考虑多回退5/10步使用混合天气
        # 混合天气的意思是几步范围内是本小时天气剩余采用下小时天气
        # curMap = self.maps[houridx]
        # if backstep == 0:
        restart = self.path[self.curNode.cost - backstep]
        # curMap = Tools.mixedMaps(restart, self.maps, MixRange)
        if hour > 20:
            return None
        curMap = Tools.endValidMixedMaps(restart, self.maps, self.stime)
        HashAstar.init()
        node = HashAstar.astarMainLoop(restart, self.endPoint, curMap)
        return node

