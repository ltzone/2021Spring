import numpy as np


class RidgeRegression:
    def __init__(self, alpha=1):
        self.coef = None
        self.alpha = alpha
        pass

    def fit(self, X, y):
        m = y.size
        X = np.hstack((np.ones((y.size, 1)), X))
        y.resize(m, 1)
        n = np.size(X, 1)

        beta = np.linalg.inv(X.T @ X + self.alpha * np.identity(n)) @ X.T @ y

        self.coef = beta

        return beta

    def predict(self, X):
        n = X.shape[0]
        X = np.hstack((np.ones((n, 1)), X))
        return (X @ self.coef).flatten()

