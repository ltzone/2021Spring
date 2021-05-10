import networkx as nx
import numpy as np
import random
import pickle
import pandas as pd
from tqdm import tqdm
from utils import *


class Node2Vec:
    def __init__(self, G, walk_length=30, walk_per_node=3, return_prob=1, in_out_prob=2):
        self.G = nx.Graph(G)
        self.walk_length = walk_length
        self.walk_per_node = walk_per_node
        self.return_prob = return_prob
        self.in_out_prob = in_out_prob

    def walk(self):
        """
        return the random walking result of all nodes.
        """
        G = self.G
        pi = self.preprocess_modified_weights()
        walks = []

        for iter in range(self.walk_per_node):
            print(f"Walk iteration {iter+1}/{self.walk_per_node}")
            for i, u in enumerate(tqdm(G.nodes)):
                walks.append(self.node2vecWalk(pi, u, self.walk_length))

        return walks

    def node2vecWalk(self, pi, u, l):
        """
        simulate a single walk with length l starting from node u based on transfer probability pi.

        return the trace of this walk
        """
        G = self.G

        walk = [u]
        for walk_iter in range(1,l):
            curr = walk[-1]
            vs_candidate = list(G.neighbors(curr))
            if len(vs_candidate) != 0:
                if len(walk) == 1: # no previous edge, uniform sampling
                    walk.append(random.sample(vs_candidate, 1)[0])
                else: # sample based on pre-computed prob vector
                    walk.append(np.random.choice(vs_candidate, p=pi[walk[-2], curr]))
            else:
                break
        return walk

    def preprocess_modified_weights(self):
        """
        preprocessing to accelerate computing

        assign a transfer probability vector to every edge (src,dst)
        so that random walk for next vertex can sample efficiently given the last walked edge
        """
        pi = dict()

        for edge in self.G.edges:
            src, dst = edge
            pi[src, dst] = self.compute_transfer_prob(src, dst)
            pi[dst, src] = self.compute_transfer_prob(dst, src)

        return pi

    def compute_transfer_prob(self, src, dst):
        """
        called by [preprocess_modified_weights] twice for an edge in undirected graph
        """
        G = self.G

        src_neighbors = set(G.neighbors(src))
        transfer_prob = np.zeros(len(list(G.neighbors(dst))))
        for i, neighbor in enumerate(G.neighbors(dst)):
            if neighbor == src:  # d_{tx} = 0
                transfer_prob[i] = 1 / self.return_prob
            elif neighbor in src_neighbors:  # d_{tx} = 1
                transfer_prob[i] = 1
            else:  # d_{tx} = 2
                transfer_prob[i] = 1 / self.in_out_prob

        return transfer_prob / transfer_prob.sum()