import numpy as np

epsilon = 1e-20

# def sigmoid(x):
#     return np.exp(-np.logaddexp(0, -x))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def loss(X, y, theta):
    m = y.size
    h = sigmoid(X @ theta)
    loss = (1 / m) * (((-y).T @ np.log(h + epsilon)) - ((1 - y).T @ np.log(1 - h + epsilon)))
    return loss


class LogisticRegression:
    def __init__(self, max_iter=100, lr=0.1):
        self.max_iter = max_iter
        self.lr = lr
        self.loss_record = np.zeros((max_iter, 1))
        self.coef = None
        pass

    def fit(self, X, y):
        m = y.size
        X = np.hstack((np.ones((y.size, 1)), X))
        y.resize(m, 1)
        n = np.size(X, 1)
        self.coef = np.random.rand(n, 1)

        for i in range(self.max_iter):
            theta = self.coef
            lr = self.lr/(1+i)
            # lr = self.lr

            self.loss_record[i] = loss(X, y, theta)
            new_coef = theta - (lr / m) * (X.T @ (sigmoid(X @ theta) - y))

            self.coef = new_coef

        return

    def predict(self, X):
        n = X.shape[0]
        X = np.hstack((np.ones((n, 1)), X))
        return np.round(sigmoid(X @ self.coef)).flatten()

