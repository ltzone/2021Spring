import cv2
import numpy as np
from utils import *


# 把目标图放在64x128的灰色图片中间，方便计算描述子
def get_hog_descriptor(image):
    image = image.reshape(32, 32, 3)
    hog = cv2.HOGDescriptor()
    h, w = image.shape[:2]
    rate = 64 / w
    image = cv2.resize(image, (64, int(rate*h)))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bg = np.zeros((128, 64), dtype=np.uint8)
    bg[:,:] = 127
    h, w = gray.shape
    dy = (128 - h) // 2
    bg[dy:h+dy,:] = gray
    descriptors = hog.compute(bg, winStride=(8, 8), padding=(0, 0))
    return descriptors


if __name__ == '__main__':
    train_X, train_y, test_X, test_y = load_data()

    feature_train = []
    for X in train_X:
        feature_train.append(get_hog_descriptor(X).flatten())
    feature_train = np.array(feature_train)
    np.save("data/feat_train_X.npy", feature_train)

    feature_test = []
    for X in test_X:
        feature_test.append(get_hog_descriptor(X).flatten())
    feature_test = np.array(feature_test)
    np.save("data/feat_test_X.npy", feature_test)

