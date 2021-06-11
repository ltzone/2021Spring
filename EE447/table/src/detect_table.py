import cv2
import os
import numpy as np

import os
import cv2


class DetectTable:
    def __init__(self, morph_size=12, min_text_height=10, max_text_height=30,
                 cell_threshold=15, min_columns=4):
        # the size to dilate the image
        self.morph_size = (morph_size, morph_size)

        # the range of box height that should be recognized as a line of text
        self.min_text_height = min_text_height
        self.max_text_height = max_text_height

        # the counting index of lines, should be fall within min_text_height/max_text_height
        self.cell_threshold = cell_threshold

        # the min columns that can be recognized as a table
        self.min_columns = min_columns

    def pre_process_image(self, img,  output_file=None):
        # get rid of the color
        pre = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Otsu threshold
        pre = cv2.threshold(pre, 250, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # dilate the text to make it solid spot
        cpy = pre.copy()
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, self.morph_size)
        cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
        pre = ~cpy

        if output_file is not None:
            cv2.imwrite(output_file, pre)
        return pre



    def find_text_boxes(self, pre):
        # Looking for the text spots contours
        # OpenCV 4
        contours, hierarchy = cv2.findContours(pre, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Getting the texts bounding boxes based on the text size assumptions
        boxes = []

        # An auxiliary information showing the range of box heights,
        # can be used to tune text_height range in the configuration
        print([cv2.boundingRect(contour)[3] for contour in contours])

        for contour in contours:
            box = cv2.boundingRect(contour)
            h = box[3]

            if self.min_text_height < h < self.max_text_height:
                boxes.append(box)

        return boxes


    def find_table_in_boxes(self, boxes):
        rows = {}
        cols = {}

        # Clustering the bounding boxes by their positions
        for box in boxes:
            (x, y, w, h) = box
            col_key = x // self.cell_threshold
            row_key = y // self.cell_threshold
            cols[row_key] = [box] if col_key not in cols else cols[col_key] + [box]
            rows[row_key] = [box] if row_key not in rows else rows[row_key] + [box]

        # Filtering out the clusters having less than 2 cols
        table_cells = list(filter(lambda r: len(r) >= self.min_columns, rows.values()))
        # Sorting the row cells by x coord
        table_cells = [list(sorted(tb)) for tb in table_cells]
        # Sorting rows by the y coord
        table_cells = list(sorted(table_cells, key=lambda r: r[0][1]))

        return table_cells


    def build_lines(self, table_cells):
        if table_cells is None or len(table_cells) <= 0:
            return [], []

        max_last_col_width_row = max(table_cells, key=lambda b: b[-1][2])
        max_x = max_last_col_width_row[-1][0] + max_last_col_width_row[-1][2]

        max_last_row_height_box = max(table_cells[-1], key=lambda b: b[3])
        max_y = max_last_row_height_box[1] + max_last_row_height_box[3]

        hor_lines = []
        ver_lines = []

        for box in table_cells:
            x = box[0][0]
            y = box[0][1]
            hor_lines.append((x, y, max_x, y))

        for box in table_cells[0]:
            x = box[0]
            y = box[1]
            ver_lines.append((x, y, x, max_y))

        (x, y, w, h) = table_cells[0][-1]
        ver_lines.append((max_x, y, max_x, max_y))
        (x, y, w, h) = table_cells[0][0]
        hor_lines.append((x, max_y, max_x, max_y))

        return hor_lines, ver_lines

    def detect(self, img, out_path, dilate_path=None):
        pre_processed = self.pre_process_image(img, dilate_path)
        text_boxes = self.find_text_boxes(pre_processed)
        cells = self.find_table_in_boxes(text_boxes)
        hor_lines, ver_lines = self.build_lines(cells)

        # Visualize the result
        vis = img.copy()

        # for box in text_boxes:
        #     (x, y, w, h) = box
        #     cv2.rectangle(vis, (x, y), (x + w - 2, y + h - 2), (0, 255, 0), 1)

        for line in hor_lines:
            [x1, y1, x2, y2] = line
            cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255), 1)

        for line in ver_lines:
            [x1, y1, x2, y2] = line
            cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255), 1)

        cv2.imwrite(out_path, vis)

if __name__ == "__main__":
    in_file = os.path.join("../image", "page1.png")
    pre_file = os.path.join("../image", "pre.png")
    out_file = os.path.join("../image", "out.png")

    img = cv2.imread(os.path.join(in_file))

    detector = DetectTable()

    detector.detect(img, out_file, pre_file)