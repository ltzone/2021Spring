import json
import random
import networkx as nx
import pandas as pd
from GraphCommunity import Louvain
import matplotlib.pyplot as plt


DG = nx.powerlaw_cluster_graph(100, 2, 0.8)
DG = nx.MultiGraph(DG)
# use larger goal cluster numbers to get better robustness
model = Louvain(DG, 5)
cluster_map = model.classify(verbose=True)


colors = ["#6699CC", "#663366", "#CCCC99", "#990033", "#CCFF66", "#FF9900", "#009933", "#0099FF", "#CCCCCC"]
color_list = [colors[cluster_map[i]] for i in DG.nodes]
plt.figure(1)
nx.draw_networkx(DG, node_color=color_list)
plt.show()

print(DG, cluster_map)

