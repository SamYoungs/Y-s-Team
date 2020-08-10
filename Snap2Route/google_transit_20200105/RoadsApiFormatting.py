import pandas as pd
import os

frame = pd.read_csv("./output1.csv")
print(frame.iloc[0]['latitude'])
# sub = frame.iloc[1]['1'] - frame.iloc[2]['1']
# print(sub)