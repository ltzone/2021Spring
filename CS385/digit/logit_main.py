from LogisticRegression import LogisticRegression
from utils import *
import matplotlib.pyplot as plt


if __name__ == '__main__':
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



