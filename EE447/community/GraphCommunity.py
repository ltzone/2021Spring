import operator
import random
import json
import time
from queue import Queue

import networkx as nx
import copy



def test_edge(G, x, y):
    try:
        _ = G[x][y]
        return 1
    except KeyError:
        return 0


def get_altas_or_not(G, x, y):
    try:
        if x == y:
            return list(G[x][y]) + list(G[x][y])
            # self loop should be count twice of degree
        else:
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

        rej_prob: double
            ranging from 0 ~ 1, reject the local move with probability
            0 means the original Louvain algorithm
            1 means reject any local changes that may lead to a contradiction to the ground truth
        """
        assert type(G) is nx.MultiGraph
        self.G = nx.MultiGraph(G)
        self.m = G.number_of_edges()
        self.cluster_map = {i: i for i in G.nodes}
        self.rev_map = {}  # a reverse table
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

        Returns
        -------
        Boolean: whether the move actually takes place, or
                 is rejected due to contradiction to ground truth
        """
        old_cluster = self.cluster_map[v]
        # move out
        self.sum_in_map[old_cluster] -= 2 * sum(len(get_altas_or_not(self.G, v, u)) for u in self.rev_map[old_cluster])
        self.sum_tot_map[old_cluster] -= self.degree_map[v]
        # move in
        self.cluster_map[v] = c
        self.rev_map[old_cluster].remove(v)
        self.rev_map[c].add(v)
        self.sum_in_map[c] += 2 * sum(len(get_altas_or_not(self.G, v, u)) for u in self.rev_map[c])
        self.sum_tot_map[c] += self.degree_map[v]
        return True

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
        Compute the modularity of current community, the derived form
        """
        modularity = 0
        for c in self.rev_map.keys():
            modularity += self.sum_in_map[c] / self.m / 2 - (self.sum_tot_map[c] / self.m / 2) ** 2
        return modularity

    def get_cluster_num(self):
        return sum(1 if len(v) != 0 else 0 for k, v in self.rev_map.items())

    def get_modularity_gain(self, v, c):
        """

        Parameters
        ----------
        v : node to be moved
        c : destination cluster

        Returns
        -------
        the actual gain of global modularity of moving one node to another cluster

        """
        old_c = self.cluster_map[v]
        c_n = c
        ki = self.degree_map[v]

        ki_i2C = 0  # the sum of the weights of links from node i to nodes in C
        ki_D2i = 0  # the sum of the weights of links from nodes in D to node i
        sum_tot_new = self.sum_tot_map[c_n]
        sum_tot_old = self.sum_tot_map[old_c]
        for u in self.G.neighbors(v):
            if self.cluster_map[u] == c_n:
                ki_i2C += 2 * len(self.G[v][u]) if v != u else 0
                # IMPORTANT TO SKIP self-edge
            if self.cluster_map[u] == old_c:
                ki_D2i += 2 * len(self.G[u][v]) if v != u else 0
        delta_Q = ki_i2C / 2 / self.m - ki_D2i / 2 / self.m - \
                  (sum_tot_new * ki / 2. / self.m / self.m) + \
                  (sum_tot_old * ki / 2. / self.m / self.m) - \
                  (self.degree_map[v] / 2 / self.m) ** 2 / 2
        return delta_Q


class Louvain:
    def __init__(self, graph, cluster_num):
        """

        Parameters
        ----------
        graph : nx.MultiGraph, the graph to be clustered
        cluster_num : the goal of clusters where the algorithm should stop
            (Note, the cluster number is not surely to be obtained, the
                algorithm may stop at any cluster larger than this number
        """
        assert (type(graph) is nx.MultiGraph)
        self.G = graph
        self.Gmod = self.G.copy()
        self.m = graph.number_of_edges()
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
        last_cluster_num = self.community.get_cluster_num()
        last_cluster_map = copy.copy(self.cluster_map)
        while True:
            print(f"Round {round_n}, {self.Gmod.number_of_edges(), self.Gmod.number_of_nodes()}")
            self.move_nodes(verbose)
            self.aggregate(verbose)
            if verbose:
                with open(f"checkpoint_{round_n}"
                          f"_{self.community.get_cluster_num()}.json", 'w') as f:
                    json.dump({int(k): int(v) for k, v in self.cluster_map.items()}, f)
            round_n += 1
            if (self.community.get_cluster_num() == last_cluster_num) or \
                    (self.community.get_cluster_num() <= self.cluster_num):
                self.cluster_map = last_cluster_map
                break
            last_cluster_num = self.community.get_cluster_num()
            last_cluster_map = copy.copy(self.cluster_map)
        with open(f"result.json", 'w') as f:
            json.dump({int(k): int(v) for k, v in self.cluster_map.items()}, f)
        return self.cluster_map

    def move_nodes(self, verbose):
        """
        Repeatedly choose random nodes and make local changes to the [community] object,
        until no nodes need modifying or the global modularity stops increasing
        """
        if verbose:
            print(f"New Phase, modularity {self.community.get_modularity()}")
        move_flag = True
        iter_cnt = 0
        last_modularity = self.community.get_modularity()
        while move_flag:
            # while there is still vertice to move or gain in modularity
            iter_cnt += 1
            moved_v = 0
            move_flag = False
            for v in random.sample(self.Gmod.nodes, self.Gmod.number_of_nodes()):
                # optimize every vertex on the graph
                # Note: Random order visiting is more efficient than "for v in self.Gmod.nodes:"
                best_q = 0
                old_c = self.community.cluster_map[v]
                best_c = self.community.cluster_map[v]
                appeared_community = []
                for n in self.Gmod.neighbors(v):
                    c_n = self.community.cluster_map[n]
                    if c_n in appeared_community:
                        continue
                    appeared_community.append(c_n)
                    delta_Q = self.community.get_modularity_gain(v, c_n)
                    if best_q < delta_Q:
                        best_q = delta_Q
                        best_c = c_n
                if int(best_c) != int(old_c):
                    is_moved = self.community.move_cluster(v, best_c)
                    if is_moved:
                        moved_v += 1
                        move_flag = True
            new_modularity = self.community.get_modularity()
            if verbose:
                print(f"Iteration #{iter_cnt}, {moved_v} vertices Moved, "
                      f"modularity: {new_modularity}, "
                      f"cluster#: {self.community.get_cluster_num()}")
            if new_modularity - last_modularity < 1e-4:
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
        self.Gmod.add_nodes_from(range(len(rev_map)))
        for (x, y, _) in self.G.edges:
            cls_idx = self.cluster_map[x]
            dst_idx = self.cluster_map[y]
            self.Gmod.add_edge(cls_idx, dst_idx)

        self.community = GraphCommunity(self.Gmod)
        if verbose:
            print(f"{idx} clusters")
