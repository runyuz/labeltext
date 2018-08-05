import numpy as np
import cv2 as cv
from PyQt5.QtGui import qRed, qGreen, qBlue
from PyQt5.QtCore import QPoint
import cProfile
import pstats

from labelme.shape import Shape

lk_params = dict( winSize  = (5, 5),
                  maxLevel = 5,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 3,
                       blockSize = 7 )
MIN_D = 3
MAX_D = 13
MAX_W = 20

velocity = 0
prev_points = None
path = None

def findMaxDistance(p):
    if len(p) < 2:
        return None
    x_min, y_min = p[0]
    x_max, y_max = p[0]
    for x,y in p[1:]:
        if x < x_min:
            x_min = x
        elif x > x_max:
            x_max = x
        if y < y_min:
            y_min = y
        elif y > y_max:
            y_max = y
    return min(x_max-x_min, y_max-y_min)

def checkedTrace(img0, img1, p0, back_threshold=1.0):
    p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
    p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
    d = abs(p0-p0r).reshape(-1, 2).max(-1)
    status = d < back_threshold

    return p1, status


def QPoints2CV(qpoints, dtype):
    points = []

    for qpoint in qpoints:
        points.append([qpoint.x(), qpoint.y()])
    cv_points = np.array(points, dtype=dtype)
    return cv_points[None,:,:]  # 返回行向量


def CV2QPoints(array):
    qpoints = []

    for (x, y) in array.tolist()[0]:
        qpoints.append(QPoint(x, y))

    return qpoints
    
def findParameter(points_list):
    # 调参工程师上线
    distance = findMaxDistance(points_list)
    if distance is None:
        return False
    distance = int(distance/4)
    distance = max(distance, MIN_D)
    win_size = min(distance, MAX_W)
    min_distance = min(distance, MAX_D)
    lk_params["winSize"] = (win_size, win_size)
    feature_params["minDistance"] = min_distance
    feature_params["blockSize"] = min_distance
    
    print("===Parameters:")
    print(lk_params)
    print(feature_params)
    return True

def translate(image, x, y):
    M = np.float32([[1, 0, x], [0, 1, y]])
    shifted = cv.warpAffine(image, M, (image.shape[1], image.shape[0]))
    return shifted

green = (0, 255, 0)
red = (0, 0, 255)

def track(src_path, dst_path, shapes):
    # pr = cProfile.Profile()
    # pr.enable()
    src = cv.imread(src_path)
    dst = cv.imread(dst_path)
    src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    dst_gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
    new_shapes = []
    for shape in shapes:
        points_list = QPoints2CV(shape.points, np.int32)

        if not findParameter(points_list[0]):
            continue
        mask = np.zeros_like(src_gray)
        mask = cv.fillPoly(mask, points_list, (255,255,255))
        p0 = cv.goodFeaturesToTrack(src_gray, mask=mask, **feature_params)
        if p0 is None or not len(p0):   # Check if no good feature exists
            continue
        p1, trace_status = checkedTrace(src_gray, dst_gray, p0)
        p0 = p0[trace_status]
        p1 = p1[trace_status]

        # for (x0, y0), (x1, y1) in zip(p0[:,0], p1[:,0]):
        #     cv.circle(dst, (x1, y1), 2, red, -1)
        #     cv.circle(dst, (x0, y0), 2, green, -1)
        # cv.imshow('emmm', dst)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        if len(p0) < 4:
           continue
        H, status = cv.findHomography(p0, p1, cv.RANSAC, 1.0)
        cv_points = cv.perspectiveTransform(np.float32(points_list), H)
        shape.points = CV2QPoints(cv_points)
        new_shapes.append(shape)
    # '''
    # pr.disable()
    # ps = pstats.Stats(pr).sort_stats('cumulative')
    # ps.print_stats()
    # '''
    return new_shapes
