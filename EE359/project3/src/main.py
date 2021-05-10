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

    # Node2Vec
    n2v = Node2Vec(G)
    walk_stat = n2v.walk()
    with open("walk_stat.pik", "wb") as f:
        pickle.dump(walk_stat, f)
    print("finish walking")

    # Word2Vec
    w2v = Word2Vec(corpus=walk_stat)
    w2v.fit(epoches=4)
    print("finish training")
    word_vectors = w2v.get_word_vector()
    with open(f"embedding_result.pik", 'wb') as f:
        pickle.dump(word_vectors, f)

    # predict link for edges
    with open("data/course3_test.csv", 'r') as f2:
        table = pd.read_csv(f2)
    predict_distance = []
    for row in table.values:
        src = row[1]
        dst = row[2]
        try:
            predict_distance.append(np.vdot(word_vectors[src], word_vectors[dst])
                                    / np.linalg.norm(word_vectors[src]) / np.linalg.norm(word_vectors[dst]))
        except KeyError:
            predict_distance.append(random.random()*2-1)

    out_df = pd.DataFrame(predict_distance, columns=['label'])
    out_df.index.name = 'id'
    out_df.to_csv('data/submission.csv')





