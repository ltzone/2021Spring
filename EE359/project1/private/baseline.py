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
    print([np.where(cluster1 == j)[0].size for j in range(5)])
    print([np.where(cluster2 == j)[0].size for j in range(5)])
    least_error = 50000
    for per in permutations([0, 1, 2, 3, 4]):
        err = 0
        for i in range(50000):
            if cluster1[i] != per[cluster2[i]]:
                err += 1
            if (err > 1000):
                break
        least_error = min(err, least_error)
    return least_error


def test_radius(input1, input2):
    with open(input1, 'r') as f:
        cluster1 = pd.read_csv(f, index_col="id")["category"]
    # with open(input2, 'r') as f:
    #     cluster2 = pd.read_csv(f, index_col="id")["category"]
    with open("../data/course1.csv", 'r') as f:
        table = pd.read_csv(f, index_col="PID").to_numpy()
    res = []
    for i in range(5):
        samples = table[np.where(cluster1 == i)]
        center = samples.mean(0)
        radius = np.max([np.linalg.norm(samples[j] - center) for j in range(samples.shape[0])])
        res.append(radius)
    print(res)


if __name__ == '__main__':
    # data_input = read_data("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/course1.csv")
    # classifier = KMeans(5)
    # classifier.fit(data_input)
    # write_result(classifier.labels_, "baseline2.csv")
    test_radius("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/result(1).csv",
                "/Users/ltzhou/GIT/2021Spring/EE359/project1/data/baseline.csv")
    print(cmp_diff("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/result.csv",
                   "/Users/ltzhou/GIT/2021Spring/EE359/project1/private/baseline.csv"))
