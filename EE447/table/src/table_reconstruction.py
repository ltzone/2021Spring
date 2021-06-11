import cv2
import os
import numpy as np
#cv2不允许有中文路径

class PicTable:
    def __init__(self):
        self.path= os.path.join(os.getcwd(), "..", "image")
        self.pic=[]

    def setImgPath(self,path):
        self.path=path

    def drawLine(self):
        # ori_pic代表原图, opt表示要进行优化的图片
        ori_pic = cv2.imread(self.path)
        opt_pic = ori_pic.copy()
        # 将图像转为灰度图,并提取边缘.
        opt_pic = cv2.cvtColor(opt_pic, cv2.COLOR_BGR2GRAY)
        edge = cv2.Canny(opt_pic, 20, 40, apertureSize=3)

        # 通过边缘来确定表格中的直线以及端点
        lines = cv2.HoughLinesP(edge, 1, np.pi / 180, threshold=200, minLineLength=200, maxLineGap=5, )
        lines = [lines[i][0] for i in range(len(lines))]

        # 擦除表格中原有的划线.并确定表格位置, box中的元素是要确定的表格左上角,和右下角的顶点
        box = [-9999, 9999, -9999, 9999]
        for x1, y1, x2, y2 in lines:
            cv2.line(opt_pic, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(ori_pic, (x1, y1), (x2, y2), (255, 255, 255), 4)
            box[0] = max(x1, x2, box[0])
            box[1] = min(x1, x2, box[1])
            box[2] = max(y1, y2, box[2])
            box[3] = min(y1, y2, box[3])

        # 去除表格的大框,即将表格线填充为白色
        cv2.rectangle(opt_pic, (box[1], box[3]), (box[0], box[2]), (255, 255, 255), 4)
        cv2.rectangle(ori_pic, (box[1], box[3]), (box[0], box[2]), (255), 4)

        # 对优化图片进行腐蚀操作以及二值化以方便处理
        kernel = np.ones((2, 2), np.uint8)
        opt_pic = cv2.erode(opt_pic, kernel, iterations=3)
        mat, opt_pic = cv2.threshold(opt_pic, 127, 255, cv2.THRESH_BINARY)
        # 取反色,这样所有空白区域的亮度值加起来是0
        opt_pic = 255 - opt_pic

        # 可以先对表格边缘做一定的扩张
        xmin = box[1] + 10
        ymin = box[3]
        xmax = box[0] - 10
        ymax = box[2]

        # 记录下我们要划的线的两个端点
        linetodraw = []

        # 我们接下来一行行扫描图像以确定划分表格的横线.
        # 若遇到某一行所有像素的亮度值之和为0,那么说明这一行没有元素,
        # 直到找到下一个像素值求和不为0的行,取这两行中间作为划分表格两行的分界线,
        # 并记录直线的两个端点(x1,y1,x2,y2)在linetodraw数组内
        while ymin <= ymax:
            if (sum(opt_pic[ymin][xmin:xmax])) == 0:
                liney = float(ymin)
                ymin += 1
                while sum(opt_pic[ymin][xmin:xmax]) == 0 and ymin <= ymax:
                    ymin += 1
                    liney += 0.5
                liney = int(liney + 0.5)
                linetodraw.append([box[1], liney, box[0], liney])
            ymin += 1
        print(linetodraw)

        for x1, y1, x2, y2 in linetodraw:
            cv2.line(ori_pic, (x1, y1), (x2, y2), (0, 0, 255), 1)

        # 同理,我们转置原来的图像,对表格的列也进行像行一样的划分.
        # 并也将直线的两端记录在linetodraw数组内
        linetodraw = []
        xmin = box[1]
        ymin = box[3] + 10
        xmax = box[0]
        ymax = box[2] - 10

        # 显示图片处理的过程
        # cv2.imshow("win", opt_pic)
        # cv2.waitKey(0)
        opt_pic = opt_pic.transpose()
        while xmin <= xmax:
            if (sum(opt_pic[xmin][ymin:ymax])) == 0:
                linex = float(xmin)
                THRES = 8
                while sum(opt_pic[xmin][ymin:ymax]) == 0 and xmin <= xmax and THRES >= 0:
                    xmin += 1
                    THRES -= 1
                    linex += 0.5
                if (THRES > 0):
                    continue
                while sum(opt_pic[xmin][ymin:ymax]) == 0 and xmin <= xmax:
                    xmin += 1
                    linex += 0.5
                linex = int(linex + 0.5)
                linetodraw.append([linex, box[3], linex, box[2]])
            xmin += 1

        print(linetodraw)
        # 在原图上画出表格分割线
        for x1, y1, x2, y2 in linetodraw:
            cv2.line(ori_pic, (x1, y1), (x2, y2), (255, 0, 0), 1)

        # 显示结果图片
        cv2.imshow("win", ori_pic)
        cv2.waitKey(0)

if __name__=="__main__":
    test = PicTable()
    #调用外部图片必须先设置图片路径
    test.setImgPath(os.path.abspath(os.path.join(os.path.join(os.getcwd(), "..", "image"),"111.JPG")))
    test.drawLine()
