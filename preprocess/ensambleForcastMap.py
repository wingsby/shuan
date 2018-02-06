# -*- coding: UTF8 -*-
# 预测天气 输出每个格点对应的天气
import pandas as pd
import numpy as np
import time

start = time.time()

path = "F:\ml\data\\"
fname = path + "ForecastDataforTesting_201802.csv"
wname=path + "ensemble_201802.csv"
data = pd.read_csv(fname, iterator=True)

loop = True
chunkSize = 10000000  # 10000000 #read 10 model

# =====================================
#    方法一
# =====================================
chunk_mean = np.empty([1, 7])

it = 0
while loop:
    # for i in range(1):
    it += 1
    try:
        chunk = data.get_chunk(chunkSize)
        aa = np.array(chunk.values)
        tmpmean = np.mean(np.reshape(aa, (int(len(aa) / 10), 10, 7)), axis=1)
        chunk_mean = np.append(chunk_mean, tmpmean, axis=0)
    # chunk.std()
    except StopIteration:
        loop = False
        print("Iteration is stopped.")
print("iteration number: ", it)
chunk_mean = np.delete(chunk_mean, 0, 0)  # 删掉第一行
df = pd.DataFrame(chunk_mean, columns=['xid', 'yid', 'date_id', 'hour', 'model', 'wind', 'rain'])  # 将list转为dataframe
df = pd.DataFrame(chunk_mean, columns=['xid', 'yid', 'date_id', 'hour', 'model', 'wind', 'rain'])  # 将list转为dataframe

df.xid = df.xid.astype(np.int64)
df.yid = df.yid.astype(np.int64)
df.date_id = df.date_id.astype(np.int64)
df.hour = df.hour.astype(np.int64)
df.model = df.model.astype(np.int64)

df.to_csv(wname, index=False)
end = time.time()
print("%f second" % (end - start))
