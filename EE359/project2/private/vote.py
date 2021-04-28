import pandas as pd

tables = []

with open("../private/labels80.csv", 'r') as f:
    tables.append(pd.read_csv(f)["category"])

with open("../private/labels77.csv", 'r') as f:
    tables.append(pd.read_csv(f)["category"])

with open("../private/labels765.csv", 'r') as f:
    tables.append(pd.read_csv(f)["category"])

labels = []
contra_cnt = 0
two_cnt = 0
for i in range(31136):
    voter = dict()
    for tab in tables:
        val = tab[i]
        if val not in voter.keys():
            voter[val] = 0
        voter[val] += 1
    voted_val = max(voter.items(), key=lambda x: x[1])
    labels.append(voted_val[0])
    if voted_val[1] != 3:
        contra_cnt += 1
    if voted_val[1] == 2:
        two_cnt += 1

print(labels, contra_cnt, two_cnt)

out_df = pd.DataFrame(labels, columns=['category'])
out_df.index.name = 'id'
out_df.to_csv('vote_labels.csv')