

from threading import Thread
from typing import Iterable


def changePath():

    import sys
    import os

    # change Directory
    os.chdir(os.path.join(os.getcwd(), '../detection_module\\'))
    print(os.getcwd())
    # add to sys path
    sys.path.append(os.getcwd())

def getBgModelAndRoad(vid):
    # changePath()
    import cv2 as cv
    # from Yolov5_DeepSort_Pytorch.track import detect
    from Road_Detection import road
    from Background_subtraction.bg import bg
    import time

    t1 = time.time()
    image = bg(vid)  # calling bgSubtract function
    while image.backgroundFrame is None:
        pass
    t2 = time.time()
    print('Time it took to get a Background Model: %.3fs' % (t2-t1))

    t1 = time.time()
    ROI, image = road.detect_road(
        image.backgroundFrame)  # calling road detection function
    t2 = time.time()
    print('Time it took to Extract Road from the Background Model: %.3fs' % (t2-t1))
    # cv.imshow("road", road_surface)
    # cv.imwrite("images/road.jpg", image)
    return image, ROI

class detection:
    def __init__(self, vid, ROI, shp):
        changePath()
        from detection_module.track import det
        import params
        import torch

        params.imgsz *= 2 if len(params.imgsz) == 1 else 1  # expand
        with torch.no_grad():
            # calling the yolov5 and deepsort module
            # initializing the detection
            self.dets = det(params, source=vid, roi=ROI, shape = shp.shape)
# NOTE: APPLY THE ROI, REUTRN THE COORDINATES OF THE WHOLE CONTOURS #DONE----------
