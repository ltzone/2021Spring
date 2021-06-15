import scipy.io as scio
import pdb
import numpy as np

if __name__ == '__main__':
    test_dir = "data/test_32x32.mat"
    test_dict = scio.loadmat(test_dir)
    test_X, test_y = test_dict["X"].T, test_dict["y"]

    train_dir = "data/train_32x32.mat"
    train_dict = scio.loadmat(train_dir)
    train_X, train_y = train_dict["X"].T, train_dict["y"]

    ## sample train
    train_index = np.random.choice(np.arange(train_y.shape[0]), 8000, replace=False)
    test_index = np.random.choice(np.arange(test_y.shape[0]), 2000, replace=False)

    np.save("data/train_X.npy", train_X[train_index])
    np.save("data/test_X.npy", test_X[test_index])
    np.save("data/train_y.npy", train_y[train_index])
    np.save("data/test_y.npy", test_y[test_index])

