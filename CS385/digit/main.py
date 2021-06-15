from LogisticRegression import LogisticRegression
from RidgeRegression import RidgeRegression
from KernelRegression import KernelRegression
from utils import *
import matplotlib.pyplot as plt


def run_logit():
    accs = []
    plt.rcParams['figure.figsize'] = [20, 15]
    plt.figure()
    for number in range(1, 11):
        train_X, train_y, test_X, test_y = load_data(number, feature=True, balance=True)

        lgr = LogisticRegression(max_iter=100, lr=10)

        lgr.fit(train_X, train_y)

        predict_y = lgr.predict(test_X)
        acc = binary_acc(predict_y, test_y)

        accs.append(acc)
        print(acc)

        loss_record = lgr.loss_record

        plt.subplot(3,4,number)
        plt.ylim(0,25)
        plt.plot(range(len(loss_record)), loss_record)
        plt.title(f"Loss Function for binary classifier {number}")
        plt.xlabel("# of Iterations")
        plt.ylabel("Loss")

    plt.show()

    print(sum(accs)/10)


def run_ridge():
    accs = []
    for number in range(1, 11):
        train_X, train_y, test_X, test_y = load_data(number, feature=True, balance=True)

        lgr = RidgeRegression(alpha=1)

        lgr.fit(train_X, train_y)

        predict_y = lgr.predict(test_X)
        acc = binary_acc(predict_y, test_y)

        accs.append(acc)
        print(acc)

    print(sum(accs) / 10)

def run_kernel():
    accs = []
    for number in range(1, 11):
        train_X, train_y, test_X, test_y = load_data(number, feature=True, balance=True)

        lgr = KernelRegression('rbf', gamma=10, alpha=1)
        # Why gamma can't be ~ 1?

        lgr.fit(train_X, train_y)

        predict_y = lgr.predict(test_X)
        acc = binary_acc(predict_y, test_y)

        accs.append(acc)
        print(acc)

    print(sum(accs) / 10)



if __name__ == '__main__':
    run_kernel()



