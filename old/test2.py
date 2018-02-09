# coding:utf-8
# @Author: wangye
# @Description:
# @Date:Created  on 20:28 2018/2/7.
# @Modify
#======================shaun=======================================
import copy
# array=dict()
# array[1]=[2,3]
# array[2]=[4,5]
#
# def fun(array):
#     # a=copy.copy(array[1])
#     a=array[1]
#     a.append(4)
#     print(len(array[1]))
#
#
# fun(array)
adict=dict()
adict[1]=[3,5,6]
adict[2]=[22,1]
adict[3]=[3,3,3,3,3,3]

items = adict.values()
items.sort(key=lambda x: len(x))
res=dict()


# c=[value for value in items]

# print(c)

def sort_by_value(d):
    items=d.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]
