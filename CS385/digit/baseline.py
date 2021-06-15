from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import RidgeClassifier
from utils import *

if __name__ == '__main__':
    accs = []
    for number in range(1, 11):
        train_X, train_y, test_X, test_y = load_data(number, feature=True, balance=True)

        lgr = LogisticRegression()
        # lgr = LinearDiscriminantAnalysis()
        # lgr = KernelRidge(kernel="rbf")
        # lgr = RidgeClassifier()

        lgr.fit(train_X, train_y)

        predict_y = lgr.predict(test_X)
        predict_y[predict_y<0.5] = 0
        predict_y[predict_y>=0.5] = 1
        acc = binary_acc(predict_y, test_y)

        accs.append(acc)
        # print(number, acc)
        print(acc)
    print(sum(accs)/10)



