import operator
import random
import json
import time

import networkx as nx
import pandas as pd


def read_data(filename='data/edges.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f)
    G = nx.MultiGraph()
    for row in table.to_numpy():
        G.add_edge(row[0], row[1])
    return G


def test_edge(G, x, y):
    try:
        _ = G[x][y]
        return 1
    except KeyError:
        return 0


def get_altas_or_not(G, x, y):
    try:
        return G[x][y]
    except KeyError:
        return []


class GraphCommunity:
    """
        A Data Structure for Storing Community Information of a nx.MultiGraph Object G

        Enables pre-computation for to quickly look-up degrees used in Louvain Algorithm
    """
    def __init__(self, G):
        """
        Parameters
        ----------
        G : nx.MultiGraph
        The current Graph to be assigned community
        """
        assert type(G) is nx.MultiGraph
        self.G = nx.MultiGraph(G)
        self.m = G.number_of_edges()
        self.cluster_map = {i: i for i in range(G.number_of_nodes())}
        self.rev_map = {} # a reverse table
        self.make_rev_map()
        self.degree_map = dict(G.degree)
        self.sum_in_map = {}  # the sum of links inside a cluster
        self.make_sum_in_map()
        self.sum_tot_map = {}  # the sum of total links to a cluster
        self.make_sum_tot_map()

    def move_cluster(self, v, c):
        """
        Move v to new cluster c, update various fields

        Parameters
        ----------
        v : vertex
        c : new cluster id
        """
        old_cluster = self.cluster_map[v]
        self.cluster_map[v] = c
        # move out
        self.sum_in_map[old_cluster] -= 2 * sum(len(get_altas_or_not(self.G, v, u)) for u in self.rev_map[old_cluster])
        # self.sum_in_map[old_cluster] -= sum(len(self.G[u][v]) for u in self.rev_map[old_cluster])
        self.sum_tot_map[old_cluster] -= self.G.degree(v)
        self.rev_map[old_cluster].remove(v)
        # move in
        self.rev_map[c].add(v)
        self.sum_in_map[c] += 2 * sum(len(get_altas_or_not(self.G, v, u)) for u in self.rev_map[c])
        # self.sum_in_map[c] += sum(len(self.G[u][v]) for u in self.rev_map[c])
        self.sum_tot_map[c] += self.G.degree(v)

    def make_sum_in_map(self):
        """
        Initialize sum_in
        """
        self.sum_in_map = {}
        for c, vs in self.rev_map.items():
            self.sum_in_map[c] = 0
            for u in vs:
                for v in vs:
                    self.sum_in_map[c] += len(get_altas_or_not(self.G, u, v))

    def make_sum_tot_map(self):
        """
        Initialize sum_tot
        """
        self.sum_tot_map = {}
        for c, vs in self.rev_map.items():
            self.sum_tot_map[c] = sum(dict(self.G.degree(vs)).values())

    def make_rev_map(self):
        """
        Initialize a reverse map (cluster id -> node sets) for cluster_map (node -> cluster id)
        """
        self.rev_map = dict()
        for k, v in self.cluster_map.items():
            if v not in self.rev_map.keys():
                self.rev_map[v] = set()
            self.rev_map[v].add(k)

    def get_modularity(self):
        """
        Returns
        -------
        Modularity for current community
        """
        modularity = 0
        old_x, old_y = -1, -1
        for (x, y, z) in self.G.edges:
            if (x, y) == (old_x, old_y):
                continue
            old_x, old_y = x, y
            if self.cluster_map[x] == self.cluster_map[y]:
                modularity += len(get_altas_or_not(self.G, x, y)) - \
                              (self.degree_map[x] * self.degree_map[y]) / 2 / self.m
        return modularity / 2 / self.m

    def get_cluster_num(self):
        return sum(1 if len(v) != 0 else 0 for k,v in self.rev_map.items())


class Louvain:
    def __init__(self, graph, cluster_num):
        assert (type(graph) is nx.MultiGraph)
        self.G = graph
        self.Gmod = self.G.copy()
        self.m = graph.number_of_nodes()
        self.cluster_num = cluster_num
        self.cluster_map = {i: i for i in self.G.nodes}
        self.community = GraphCommunity(graph)

    def classify(self, verbose=False):
        """
        Run the Louvain Algorithm for clustering
        Parameters
        ----------
        verbose : print verbose information
        """
        round_n = 0
        while self.community.get_cluster_num() > self.cluster_num:
            print(f"Round {round_n}")
            self.move_nodes(verbose)
            self.aggregate(verbose)
            if verbose:
                with open(f"tmp/new1_checkpoint_{round_n}"
                          f"_{self.community.get_cluster_num()}.json", 'w') as f:
                    json.dump({int(k): int(v) for k, v in self.community.cluster_map.items()}, f)
            round_n += 1
        with open(f"tmp/result.json", 'w') as f:
            json.dump({int(k): int(v) for k, v in self.community.cluster_map.items()}, f)

    def move_nodes(self, verbose):
        """
        Repeatedly choose random nodes and make local changes to the [community] object,
        until no nodes need modifying or the global modularity stops increasing
        """
        if verbose:
            print(f"New Phase, modularity {self.community.get_modularity()}")
        move_flag = True
        iter_cnt = 0
        last_modularity = -1
        while move_flag:
            iter_cnt += 1
            moved_v = 0
            move_flag = False
            for v in random.sample(self.Gmod.nodes, self.Gmod.number_of_nodes()):
                best_q = float('-inf')
                best_c = self.community.cluster_map[v]
                appeared_community = []
                for n in self.Gmod.neighbors(v):
                    c_n = self.community.cluster_map[n]
                    if c_n == best_c:
                        continue
                    if c_n in appeared_community:
                        continue
                    appeared_community.append(c_n)
                    ki = self.community.degree_map[v]
                    ki_in_gain = 0  # the sum of the weights of links from node i to nodes in C
                    ki_in_loss = 0
                    sum_tot_new = self.community.sum_tot_map[c_n]
                    sum_tot_old = self.community.sum_tot_map[best_c]
                    for u in self.Gmod.neighbors(v):
                        if self.community.cluster_map[u] == c_n:
                            ki_in_gain += len(G[v][u])
                        if self.community.cluster_map[u] == best_c:
                            ki_in_loss += len(G[v][u])
                    ki_in_gain = ki_in_gain / 2. / self.m
                    ki_in_loss = ki_in_loss / 2. / self.m

                    delta_Q = ki_in_gain - ki_in_loss \
                              - (sum_tot_new * ki / 2. / self.m / self.m) \
                              + (sum_tot_old * ki / 2. / self.m / self.m)

                    if best_q < delta_Q:
                        best_q = delta_Q
                        best_c = c_n
                if best_c != self.community.cluster_map[v]:
                    moved_v += 1
                    self.community.move_cluster(v, best_c)
                    move_flag = True
            new_modularity = self.community.get_modularity()
            if verbose:
                print(f"Iteration #{iter_cnt}, {moved_v} vertices Moved, "
                      f"modularity: {new_modularity}, "
                      f"cluster#: {self.community.get_cluster_num()}")
            if new_modularity < last_modularity:
                break
            last_modularity = new_modularity

    def aggregate(self, verbose):
        """
        Based on the [community] results, re-map the nodes into clusters

        remove redundant clusters (empty set) and re-index the cluster numbers

        create a new aggregated MultiGraph [Gmod] for the next phase
        """
        # remap the clusters for all original nodes
        new_cluter_map = dict()
        for (k, v) in self.cluster_map.items():
            new_cluter_map[k] = self.community.cluster_map[v]
        # make a reversed map
        rev_map = dict()
        for k, v in new_cluter_map.items():
            if v not in rev_map.keys():
                rev_map[v] = set()
            rev_map[v].add(k)
        # clean 0 map
        self.cluster_map = {}
        idx = 0
        for (c, vs) in (rev_map.items()):
            if len(vs) == 0:
                continue
            for v in vs:
                self.cluster_map[v] = idx
            idx += 1
        # make a new Graph based on the current cluster_map
        self.Gmod = nx.MultiGraph()
        self.Gmod.add_nodes_from(range(len(self.cluster_map)))
        for (x, y, _) in self.G.edges:
            cls_idx = self.cluster_map[x]
            dst_idx = self.cluster_map[y]
            self.Gmod.add_edge(cls_idx, dst_idx)
        self.community = GraphCommunity(self.Gmod)
        if verbose:
            print(f"{idx} clusters")


G = read_data("../data/edges.csv")
model = Louvain(G, 5)
# model = RandomLouvain(G, 5)
model.classify(verbose=True)
