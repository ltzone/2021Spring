import json
import random
import networkx as nx
import pandas as pd
from GraphCommunity import Louvain

def read_data(filename='data/edges.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f)
    G = nx.MultiGraph()
    for row in table.to_numpy():
        G.add_edge(row[0], row[1])
    return G

# with open("result.json","r") as f:
#     cluster_map = json.load(f)
#     cluster_map = {int(k):int(v) for k,v in cluster_map.items()}

with open("data/ground_truth.csv", 'r') as f:
    table = pd.read_csv(f)

DG = read_data("data/edges.csv")
# use larger goal cluster numbers to get better robustness
model = Louvain(DG, 10, {int(row[0]):int(row[1]) for row in table.values}, rej_prob=0.2)
cluster_map = model.classify(verbose=True)

# cluster_map -> truth_map
label_map = dict() # count occurences

# assign cluster to a 0~5 category
for row in table.values:
    cluster = cluster_map[row[0]]
    truth = row[1]
    if cluster not in label_map.keys():
        label_map[cluster] = dict()
    if truth not in label_map[cluster].keys():
        label_map[cluster][truth] = 0
    label_map[cluster][truth] += 1
print(label_map)

# make a dict mapping nodes to its (determinately) predicted clusters
new_label_map = dict()
for k,v_map in label_map.items():
    new_label_map[k] = 0
    for res, cnt in v_map.items():
        if cnt > new_label_map[k]:
            new_label_map[k] = res
print(new_label_map)

# assign predicted value to labels
id = 0
unknown_cnt = 0
labels = []
while id in cluster_map.keys():
    try:
        # if id has determinate cluster, assign directly
        labels.append(new_label_map[cluster_map[id]])
    except KeyError: # no cluster is found
        # otherwise, vote by degree on its neighbors' known clusters
        votes = {}
        for u in DG.neighbors(id):
            u_com = cluster_map[u]
            if u_com in new_label_map.keys():
                if new_label_map[u_com] not in votes.keys():
                    votes[new_label_map[u_com]] = 0
                votes[new_label_map[u_com]] += 1
        max_vote_label, max_vote_num = 0, 0
        for label, vote_num in votes.items():
            if vote_num > max_vote_num:
                max_vote_num = vote_num
                max_vote_label = label
        labels.append(max_vote_label)
        unknown_cnt += 1
    id += 1


out_df = pd.DataFrame(labels, columns=['category'])
out_df.index.name = 'id'
out_df.to_csv('data/labels.csv')

print(unknown_cnt)
