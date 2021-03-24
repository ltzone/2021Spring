import pandas as pd
import random
import numpy as np


def read_data(filename='data/course1.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f, index_col="PID")
    return table


class KMeans:
    def __init__(self, data, k, max_rounds, tolerance=0, **kwargs) -> None:
        """

        """
        self.data = data.to_numpy()
        self.data = self.data / self.data.max(axis=0) # normalize
        self.k = k
        self.sample_cnt = data.shape[0]
        self.dimension_cnt = data.shape[1]
        # initial_center_idx = [random.randrange(self.sample_cnt) for i in range(k)]
        self.centers = self.disperse_initials()
        print(self.centers)
        self.max_rounds = max_rounds
        self.centroid_of = np.random.randint(0, 5, self.sample_cnt)
        self.tolerance = tolerance

    def disperse_initials(self):
        centers = self.data[random.randrange(self.sample_cnt)].reshape(1,self.dimension_cnt)
        while len(centers) < self.k:
            dist = [np.average([np.linalg.norm(centers[i] - self.data[j]) for i in range(len(centers))])
                    for j in range(self.sample_cnt)]
            centers = np.append(centers, self.data[np.where(max(dist))], axis=0)
        return centers

    def cluster(self, verbose=False):
        for i in range(self.max_rounds):
            if verbose:
                print(f"Training for the {i}th round")
            old_category = np.copy(self.centroid_of)
            for (k, sample) in enumerate(self.data):
                # set centroid for every data sample
                dist = [np.linalg.norm(sample - self.centers[j]) for j in range(self.k)]
                self.centroid_of[k] = dist.index(min(dist))

            if verbose and i % 20 == 0:
                self.write_result(f"../data/checkpoint_{i}.csv")

            if self.converge(old_category, self.centroid_of, verbose):
                pass

            for j in range(self.k):
                cluster_samples = self.data[np.where(self.centroid_of == j)]  # samples that are in the j_th category
                self.centers[j] = cluster_samples.mean(0) if cluster_samples.size != 0 \
                    else np.random.random(self.dimension_cnt) # update centroids based on data samples

    def converge(self, old_category, new_category, verbose):
        error = sum(old_category - new_category != 0)
        if verbose:
            print(f"{error} samples are re-clustered")
        return error <= self.tolerance

    def preview_result(self):
        print("---------- Centroid points ----------")
        print(self.centers)
        print("---------- Cluster Results ----------")
        print(self.centroid_of)

    def write_result(self, output_dir):
        df = pd.Series(self.centroid_of, name="category")
        with open(output_dir, 'w') as f:
            df.to_csv(f, index_label="id")


if __name__ == '__main__':
    data_input = read_data("/Users/ltzhou/GIT/2021Spring/EE359/project1/data/course1.csv")
    classifier = KMeans(data_input, 5, 200)
    classifier.cluster(verbose=True)
    classifier.write_result("../data/result.csv")
