import numpy as np
import cv2 as cv
from PyQt5.QtGui import qRed, qGreen, qBlue
from PyQt5.QtCore import QPoint
import cProfile
import pstats

from labelme.shape import Shape

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

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
        mask = np.zeros_like(src_gray)
        mask = cv.fillPoly(mask, QPoints2CV(shape.points, np.int32), (255,255,255))
        p0 = cv.goodFeaturesToTrack(src_gray, mask=mask, **feature_params)
        p1, trace_status = checkedTrace(src_gray, dst_gray, p0)
        p0 = p0[trace_status]
        p1 = p1[trace_status]
        '''
        for (x0, y0), (x1, y1) in zip(p0[:,0], p1[:,0]):
            cv.circle(frame, (x1, y1), 2, red, -1)
            cv.circle(frame, (x0, y0), 2, green, -1)
        cv.imshow('emmm', frame)
        '''
        if len(p0) < 4:
            continue
        H, status = cv.findHomography(p0, p1, cv.RANSAC, 10.0)
        cv_points = cv.perspectiveTransform(QPoints2CV(shape.points, np.float32), H)
        shape.points = CV2QPoints(cv_points)
        new_shapes.append(shape)
    '''
    pr.disable()
    ps = pstats.Stats(pr).sort_stats('cumulative')
    ps.print_stats()
    '''
    return new_shapes
