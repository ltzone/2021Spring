import pandas as pd
import random
import numpy as np


def read_data(filename='data/course1.csv'):
    with open(filename, 'r') as f:
        table = pd.read_csv(f, index_col="PID")
    return table


class KMeans:
    def __init__(self, data, k, max_rounds, tolerance=0, is_kmeans_pp=True) -> None:
        """
        The encapsulation of a K-Means clustering algorithm
        a typical workflow of this class is to initialize it with data and configs
        call KMeans.cluster() to train
        call KMeans.write_result(output_dir) to output the result

        Parameters
        ----------
        data : pd.DataFrame
            input data, dimensions in columns, samples in rows
        k : int
            cluster number
        max_rounds : int
            maximum iteration rounds
        tolerance : int
            stop when two iterations produce results with differences less than tolerence
        is_kmeans_pp : bool
            use K-Means++ for initial points selection
        """
        self.data = data.to_numpy()
        # self.data = self.data / (np.abs(self.data).max(axis=0))  # normalize
        self.k = k
        self.sample_cnt = self.data.shape[0]
        self.dimension_cnt = self.data.shape[1]
        if is_kmeans_pp:
            self.centers = self._kmeans_plus_plus()
        else:
            initial_center_idx = [random.randrange(self.sample_cnt) for _ in range(k)]
            self.centers = self.data[initial_center_idx]
            # self.centers = np.random.random((self.k, self.dimension_cnt))
        # print(self.centers)
        self.max_rounds = max_rounds
        self.centroid_of = np.random.randint(0, 5, self.sample_cnt)
        self.tolerance = tolerance

    def cluster(self, verbose=False):
        """
        training the model
        Parameters
        ----------
        verbose : bool
            whether to print verbose information on console when training
        """
        for i in range(self.max_rounds):
            if verbose:
                print(f"Training for the {i}th round")
            old_category = np.copy(self.centroid_of)
            for (k, sample) in enumerate(self.data):
                # set centroid for every data sample
                dist = [np.linalg.norm(sample - self.centers[j]) for j in range(self.k)]
                self.centroid_of[k] = dist.index(min(dist))

            if verbose and i > 0 and i % 10 == 0:
                print(f"Checkpoint at {i}th round")
                self.write_result(f"data/checkpoint_{i}.csv")
                self._preview_result()

            if self._converge(old_category, self.centroid_of, verbose):
                break

            for j in range(self.k):
                cluster_samples = self.data[np.where(self.centroid_of == j)]  # samples that are in the j_th category
                self.centers[j] = cluster_samples.mean(0) if cluster_samples.size != 0 else \
                    self.data[random.randrange(self.sample_cnt)]  # update centroids based on data samples
                # in case of cluster_sample is empty for one category, randomly choose a data point as the new centroid
        if verbose:
            print("---- End of training -----")
        self._post_processing(verbose)

    def write_result(self, output_dir):
        df = pd.Series(self.centroid_of, name="category")
        with open(output_dir, 'w') as f:
            df.to_csv(f, index_label="id")

    def _kmeans_plus_plus(self):
        """
        Implementation of K-Means++ to select good initial centroids
        Returns
        -------
        An (k, n-dim) ndarray of initial centroids
        """
        fst_idx = random.randrange(self.sample_cnt)
        selected_centers = {fst_idx}
        centers = self.data[fst_idx].reshape(1, self.dimension_cnt)
        while len(centers) < self.k:
            # compute the distance of x and its nearest chosen centers
            dist = [np.min([np.linalg.norm(centers[i] - self.data[j]) for i in range(len(centers))])
                    for j in range(self.sample_cnt)]
            dist = np.multiply(dist, dist)  # D(x)^2
            dist_prob = dist / dist.sum()
            sample_idx = np.random.choice(np.arange(0, self.sample_cnt), p=dist_prob)
            if sample_idx not in selected_centers:
                centers = np.append(centers, self.data[sample_idx].reshape(1, self.dimension_cnt), axis=0)
        return centers

    def _converge(self, old_category, new_category, verbose):
        """
        Judge the difference of two iteration results
        """
        error = sum(old_category - new_category != 0)
        if verbose:
            print(f"{error} samples are re-clustered")
        return error <= self.tolerance

    def _summary(self):
        radius_list = []
        for i in range(self.k):
            category_samples = self.data[np.where(self.centroid_of == i)]
            radius = np.max(category_samples - self.centers[i])
            radius_list.append((radius, len(category_samples), i))
        return radius_list

    def _preview_result(self):
        print("----- K-Means Result -----")
        for (r, n, i) in self._summary():
            print(f"Category {i} \t {n} elements, \t radius {r}")

    def _post_processing(self, verbose=False):
        """
        Sort the results to meet the submit guideline
        """
        radius_list = []
        for i in range(self.k):
            category_samples = self.data[np.where(self.centroid_of == i)]
            category_center = category_samples.mean(0)
            radius = max([np.linalg.norm(category_samples[j] - category_center) for j in range(category_samples.shape[0])])
            radius_list.append((radius, len(category_samples), i))
        radius_list.sort(key=lambda x: x[0])
        idx_map = {old_idx: new_idx for new_idx, (_, _, old_idx) in enumerate(radius_list)}
        if verbose:
            print("----- K-Means Result -----")
            for (r, n, i) in radius_list:
                print(f"Category {idx_map[i]} \t {n} elements, \t radius {r}")
        for i in range(self.sample_cnt):
            self.centroid_of[i] = idx_map[self.centroid_of[i]]


if __name__ == '__main__':
    data_input = read_data("../data/course1.csv")
    classifier = KMeans(data_input, 5, 200, is_kmeans_pp=True)
    classifier.cluster(verbose=True)
    classifier.write_result("../data/result.csv")
