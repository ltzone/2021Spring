import operator
import random

import networkx as nx
import pandas as pd


def read_data(filename='data/edges.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f)
    G = nx.DiGraph()
    for row in table.to_numpy():
        G.add_edge(row[0], row[1])
    return G


def get_edge_or_not(G, x, y):
    try:
        return G[x, y]
    except KeyError:
        return None


def get_weight_or_not(G, x, y):
    if get_edge_or_not(G, x, y) is None:
        return 0
    else:
        return get_edge_or_not(G, x, y)["weight"]


class RandomLouvain:
    def __init__(self, graph, cluster_num):
        assert (type(graph) is nx.DiGraph)
        self.G = graph
        self.cluster_num = cluster_num
        self.Gmod = graph.copy()
        for (src, dst) in self.Gmod.edges:
            self.G.edges[src, dst]["weight"] = 1
            self.Gmod.edges[src, dst]["weight"] = 1
        self.cluster_map = {i: i  for i in self.G.nodes}
        self.rev_map = {i: {i} for i in self.G.nodes}


    def classify(self, verbose=False):
        round_n = 0
        while self.Gmod.number_of_nodes() > self.cluster_num:
            print(f"Round {round_n}")
            self.move_nodes(verbose)
            self.aggregate(verbose)
            round_n += 1

    def move_nodes(self, verbose):
        move_flag = True
        moved_v = 0
        while move_flag:
            move_flag = False
            v = random.choice(list(self.Gmod.nodes))
            best_q = float('-inf')
            best_c = self.cluster_map[v]
            for n in self.Gmod.successors(v):
                c_n = self.cluster_map[n] # calculate Q_gain for node v and cluster n (c_n)
                ki = self.G.in_degree(v, weight="weight")
                # the sum of the weights (i.e., degree) of all links to node v
                e_ic = sum([get_weight_or_not(self.G, v, u)
                            for u in self.rev_map[c_n]])
                # the sum of the weights of the links between node v and community c_n
                sum_tot = sum([v for k, v in
                              dict(self.G.in_degree(self.rev_map[c_n], weight="weight")).items()])
                # the sum of the weights of the links inside c_n
                gain_q = e_ic - ki * sum_tot / 2 / self.G.number_of_edges()
                if best_q < gain_q:
                    best_q = gain_q
                    best_c = c_n
            if best_c != self.cluster_map[v]:
                moved_v += 1
                self.rev_map[self.cluster_map[v]].remove(v)
                self.cluster_map[v] = best_c
                self.rev_map[best_c].add(v)
                move_flag = True
        if verbose:
            print(f"{moved_v} vertices Moved")

    def aggregate(self, verbose):
        self.cluster_map = {}
        for i, (_, vs) in enumerate(self.rev_map.items()):
            for v in vs:
                self.cluster_map[v] = i
        self.rev_map = {}
        for k, v in self.cluster_map.items():
            if v not in self.rev_map.keys():
                self.rev_map[v] = set()
            self.rev_map[v].add(k)
        if verbose:
            print(f"{len(self.rev_map)} clusters")

        # redraw Gmod
        self.Gmod = nx.DiGraph()
        self.Gmod.add_nodes_from(range(len(self.cluster_map)))
        for (v, cls_idx) in self.cluster_map.items():
            for u in self.G.successors(v):
                dst_idx = self.cluster_map[u]
                e = get_edge_or_not(self.Gmod, cls_idx, dst_idx)
                if e is None:
                    self.Gmod.add_edge(cls_idx, dst_idx, weight=1)
                else:
                    self.Gmod[cls_idx, dst_idx] += 1





G = read_data("../data/edges.csv")
model = RandomLouvain(G, 5)
model.classify(verbose=True)
print(G.number_of_edges(), G.number_of_nodes())
