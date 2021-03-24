from itertools import permutations

import pandas as pd
import random
import numpy as np
from sklearn.cluster import KMeans


def read_data(filename='data/course1.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f, index_col="PID")
    return table


def write_result(data, output_dir):
    df = pd.Series(data, name="category")
    with open(output_dir, 'w') as f:
        df.to_csv(f, index_label="id")


def cmp_diff(input1, input2):
    with open(input1, 'r') as f:
        cluster1 = pd.read_csv(f, index_col="id")["category"]
    with open(input2, 'r') as f:
        cluster2 = pd.read_csv(f, index_col="id")["category"]
    least_error = 50000
    for per in permutations([0, 1, 2, 3, 4]):
        err = 0
        for i in range(50000):
            if per[cluster1[i]] != cluster2[i]:
                err += 1
            if (err > 10000):
                break
        least_error = min(err, least_error)
    return least_error


if __name__ == '__main__':
    # data_input = read_data("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/course1.csv")
    # classifier = KMeans(5)
    # classifier.fit(data_input)
    # write_result(classifier.labels_, "baseline2.csv")
    print (cmp_diff("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/checkpoint_40.csv",
                    "/Users/ltzhou/GIT/2021Spring/EE359/project1/src/baseline2.csv"))
