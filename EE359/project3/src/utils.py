import networkx as nx
import pandas as pd
import random
import numpy as np


def read_data(filename='data/course3_edge.csv'):
    """
    Read the Graph
    """
    with open(filename, 'r') as f:
        table = pd.read_csv(f)
    G = nx.Graph()
    for row in table.to_numpy():
        G.add_edge(row[0], row[1])
    return G


def split_graph_cross_validation(G, folds=5):
    """
    Split the edges of the graph into several folds.

    One fold will be extracted from the graph as truth edges to be tested.

    The split results will be returned as a list of (nx.Graph, list edges)
    """
    shuffled_edges = list(G.edges)
    random.shuffle(shuffled_edges)
    fold_length = int(len(shuffled_edges) / folds) + 1
    edge_folds = [shuffled_edges[i:i + fold_length]
                  for i in range(0, len(shuffled_edges), fold_length)]

    cv_set = []
    for i in range(folds):
        G = nx.Graph()
        for fold in edge_folds[:i]:
            G.add_edges_from(fold)
        for fold in edge_folds[i + 1:]:
            G.add_edges_from(fold)
        cv_set.append((G, edge_folds[i][:]))

    return cv_set


def tied_rank(x):
    """
    Computes the tied rank of elements in x.
    This function computes the tied rank of elements in x.

    The return value is a list of numbers indicating the tied rank f each element in x
    """
    sorted_x = sorted(zip(x, range(len(x))))
    r = [0 for k in x]
    cur_val = sorted_x[0][0]
    last_rank = 0
    for i in range(len(sorted_x)):
        if cur_val != sorted_x[i][0]:
            cur_val = sorted_x[i][0]
            for j in range(last_rank, i):
                r[sorted_x[j][1]] = float(last_rank + 1 + i) / 2.0
            last_rank = i
        if i == len(sorted_x) - 1:
            for j in range(last_rank, i + 1):
                r[sorted_x[j][1]] = float(last_rank + i + 2) / 2.0
    return r


def auc(actual, posterior):
    """
    Computes the area under the receiver-operater characteristic (AUC)
    for binary classification.
    """
    r = tied_rank(posterior)
    num_positive = len([0 for x in actual if x == 1])
    num_negative = len(actual) - num_positive
    sum_positive = sum([r[i] for i in range(len(r)) if actual[i] == 1])
    auc = ((sum_positive - num_positive * (num_positive + 1) / 2.0) /
           (num_negative * num_positive))
    return auc


def get_evaluate_data(G, embedding, test_edges):
    """
    generate test edges and compute similarities.
    Input the graph, a dict of node to its embedding vectors and a list of (src, dst) truth edges,

    The function will randomly generate a group of edges that are not on the graph as false samples,

    then it will return a list of computed cosine similarities and a list of truth labels
    (0/1) for the test_edges + false samples.
    """
    scores = []
    truth = []
    false_cnt = 0
    fall_out = 0
    for edge in test_edges:
        src, dst = edge
        if src in embedding.keys() and dst in embedding.keys():
            scores.append(np.vdot(embedding[src], embedding[dst])
                          / np.linalg.norm(embedding[src]) / np.linalg.norm(embedding[dst]))
            truth.append(1)
        else:
            scores.append(random.random() * 2 - 1)
            truth.append(1)
            fall_out += 1
    print(f"{fall_out} edges in the truth don't have nodes with embedding, assigned with random distance")
    fall_out = 0
    while false_cnt < len(test_edges):
        src, dst = random.sample(G.nodes, 2)
        if (src, dst) not in G.edges and src in embedding.keys() and dst in embedding.keys():
            scores.append(np.vdot(embedding[src], embedding[dst]) / np.linalg.norm(embedding[src]) / np.linalg.norm(
                embedding[dst]))
            truth.append(0)
            false_cnt += 1
        else:
            scores.append(random.random() * 2 - 1)
            truth.append(0)
            fall_out += 1
    print(f"{fall_out} edges in the false samples don't have nodes with embedding, assigned with random distance")
    return scores, truth
