import Tools
import astar.HashAstar

# 寻路失败后回退后重试ASTAR，此时使用当前map直至ASTAR完成
# 其搜索能力很接近ASTAR，相当于局部ASTAR
from astar import HashAstar

MixRange = 10


class BackRestartModel:
    def __init__(self, curNode, endPoint, maps):
        self.curNode = curNode
        self.endPoint = astar.Node(endPoint.x, endPoint.y)
        self.maps = maps
        self.path = Tools.make_path(self.curNode)


    # 在较为极端的情况下无法完成寻路任务
    def doBackAndPlan(self):
        backstep = self.curNode.cost % 30
        houridx = self.curNode.cost / 30
        restart = self.path(self.curNode.cost - backstep)
        # 当切换时次时出错，此时应该如何？
        # 可以考虑多回退5/10步使用混合天气
        # 混合天气的意思是几步范围内是本小时天气剩余采用下小时天气
        curMap = self.maps[houridx]
        if backstep == 0:
            restart = self.path(self.curNode.cost - backstep)
            curMap = Tools.mixedMaps(restart, self.maps, MixRange)
        HashAstar.init()
        node = HashAstar.astarMainLoop(restart, self.endPoint, curMap)
        return node
