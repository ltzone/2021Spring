import json
import random
import networkx as nx
import pandas as pd
import numpy as np
import pickle
from utils import *
from Node2Vec import Node2Vec
from Word2Vec import Word2Vec

if __name__ == '__main__':
    G = read_data("data/course3_edge.csv")
    # remove 20% edges from G as test-set, node2vec on the remaining graph
    G, test_edges = split_graph_cross_validation(G,5)[0]

    # Node2Vec
    n2v = Node2Vec(G)
    walk_stat = n2v.walk()
    with open("walk_stat_cv.pik", "wb") as f:
        pickle.dump(walk_stat, f)
    print("finish walking")

    # Word2Vec
    w2v = Word2Vec(corpus=walk_stat)
    w2v.fit(epoches=5)
    print("finish training")
    word_vectors = w2v.get_word_vector()
    with open(f"embedding_result_cv.pik", 'wb') as f:
        pickle.dump(word_vectors, f)

    score, truth = get_evaluate_data(G, word_vectors, test_edges)
    # the AUC on the input of truth edge labeld 1 and same size of random edges labeled 0
    print(auc(truth, score))
    # an execution of AUC after 2 epoches of w2v is 0.937830, takes 12 mins