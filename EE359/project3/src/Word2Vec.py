import json

import numpy as np
import pickle
import random
from tqdm import tqdm


def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def init_vector(dim: int) -> np.ndarray:
    rng = np.random.default_rng()
    return (rng.random(dim) - 0.5) / dim


class Word2Vec:
    """
    Word2Vec CBOW implementation with negative sampling
    """

    def __init__(self, corpus, dimensions=50, learning_rate=0.025, window_size=2, k=5, verbose=True):
        """
        params:

        corpus:         a list of list of words for training
        dimensions:     the size of hidden layer or the size of the word vector
        learning_rate:  the learning rate for the first epoch
        window_size:    the number of neighbors in a walk trace to be considered will be twice this number
        k:              the number of negative samples for an update
        """
        self.n = dimensions
        self.lr = learning_rate
        self.window_size = window_size
        self.window_offset = list(range(-window_size, 0)) + list(range(1, window_size + 1))
        self.k = k              # negative sample number for every word
        self.corpus = corpus
        self.vocab = {}
        self.theta = {}
        self.verbose = verbose
        self._initialize_corpus()

    def _initialize_corpus(self):
        """
        initialize the word vector and model parameter to be trained for all nodes
        """
        vocab = self.vocab  # vocab is the word vector
        theta = self.theta  # theta is the model parameter
        corpus = self.corpus

        for line in corpus:
            for word in line:
                if word not in vocab:
                    vocab[word] = init_vector(self.n)
                    theta[word] = init_vector(self.n)

        if self.verbose:
            print(f"{len(vocab)} words have been loaded")

    def fit(self, epoches=5):
        """
        train the model with negative sampling, for every epoch the corpus will be traversed once.
        """
        vocab = self.vocab  # vocab is the word vector
        theta = self.theta  # theta is the model parameter
        corpus = self.corpus

        for epoch in range(1, epoches+1):
            lr = self.lr * (1 / epoch)
            for line in tqdm(corpus):
                for pos in range(2, len(line) - 2):
                    # fetch the words for the current iterations from the global dict
                    current_x = vocab[line[pos]]  # x_{w_0}
                    current_theta = theta[line[pos]]  # x_{w_0}
                    context_x = [vocab[line[pos + ofs]] for ofs in self.window_offset]
                    context_theta = [theta[line[pos + ofs]] for ofs in self.window_offset]
                    negative_words = random.choices(list(vocab), k=self.k)
                    negative_x = [vocab[word] for word in negative_words]
                    negative_theta = [theta[word] for word in negative_words]
                    x_w0 = sum(context_x) / len(context_x)
                    e = 0

                    # current: positive sample, y_current = 1
                    f = sigmoid(x_w0.dot(current_theta.T))
                    g = (1 - f) * lr
                    e = e + g * current_theta
                    current_theta = current_theta + g * x_w0

                    # negative samples, y_current = 0
                    for i in range(len(negative_x)):
                        f = sigmoid(x_w0.dot(negative_theta[i].T))
                        g = - f * lr
                        e = e + g * negative_x[i]
                        negative_theta[i] = negative_x[i] + g * x_w0

                    # update context's word vector
                    for i in range(len(context_x)):
                        context_x[i] = context_x[i] + e

                    # update back to the global dict
                    vocab[line[pos]] = current_x  # x_{w_0}
                    theta[line[pos]] = current_theta  # x_{w_0}
                    for i, ofs in enumerate([-2, -1, 1, 2]):
                        vocab[line[pos + ofs]] = context_x[i]
                        theta[line[pos + ofs]] = context_theta[i]
                    for i, word in enumerate(negative_words):
                        vocab[word] = negative_x[i]
                        theta[word] = negative_theta[i]

            if self.verbose:
                with open(f"./checkpoint_{epoch}.pik", 'wb') as f:
                    pickle.dump((vocab, theta), f)

    def get_word_vector(self):
        return self.vocab
