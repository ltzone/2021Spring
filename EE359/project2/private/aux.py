import json
import pandas as pd

with open("../private/labels.csv", 'r') as f:
    ref_table = pd.read_csv(f)

with open("../tmp/labels.csv", 'r') as f:
    my_table = pd.read_csv(f)

cnt = 0
for i in range(len(ref_table.values)):
    if ref_table.values[i][1] != my_table.values[i][1]:
        cnt+=1

print(cnt)