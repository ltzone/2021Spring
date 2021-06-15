import numpy as np
import os
from collections import Counter


def load_data(class_num=None, feature=False, balance=False, dir="data"):
    if feature:
        train_X = np.load(os.path.join(dir, "feat_train_X.npy"))
        test_X = np.load(os.path.join(dir, "feat_test_X.npy"))
    else:
        train_X = np.load(os.path.join(dir, "train_X.npy"))
        test_X = np.load(os.path.join(dir, "test_X.npy"))
        train_X = train_X.reshape((train_X.shape[0], 32 * 32 * 3))
        test_X = test_X.reshape((test_X.shape[0], 32 * 32 * 3))
    train_y = np.load(os.path.join(dir, "train_y.npy")).astype(int)
    test_y = np.load(os.path.join(dir, "test_y.npy")).astype(int)

    if class_num is not None:
        class_num = int(class_num)
        test_y[test_y != class_num] = 0
        train_y[train_y != class_num] = 0
        train_y[train_y == class_num] = 1
        test_y[test_y == class_num] = 1

    if balance:
        pos_train_cnt = np.count_nonzero(train_y)
        pos_train_idx = np.where(train_y == 1)[0]
        neg_train_idx = np.where(train_y == 0)[0]
        np.random.seed(0)
        new_train_index = np.random.choice(neg_train_idx, pos_train_cnt, replace=False)
        train_X = train_X[np.concatenate([pos_train_idx,new_train_index])]
        train_y = train_y[np.concatenate([pos_train_idx,new_train_index])]
        pos_test_cnt = np.count_nonzero(test_y)
        pos_test_idx = np.where(test_y == 1)[0]
        neg_test_idx = np.where(test_y == 0)[0]
        np.random.seed(0)
        new_test_index = np.random.choice(neg_test_idx, pos_test_cnt, replace=False)
        test_X = test_X[np.concatenate([pos_test_idx, new_test_index])]
        test_y = test_y[np.concatenate([pos_test_idx, new_test_index])]

    return train_X, train_y.flatten(), \
           test_X, test_y.flatten()


def binary_acc(predict, truth):
    return sum(predict == truth)/predict.size

if __name__ == '__main__':
    train_X, train_y, test_X, test_y = load_data()
    print(Counter(train_y.tolist()))
    print(Counter(test_y.tolist()))
    print(test_y.shape)
