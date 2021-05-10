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
    # Load embedding directly into word_vectors
    with open(f"data/pretrained_embedding.pik", 'rb') as f1:
        word_vectors = pickle.load(f1)

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
