

from multiprocessing import Process, Queue
import multiprocessing
from threading import Thread
from typing import Iterable
from winreg import QueryInfoKey


# IMAGE, ROI = None, None
qInfo = {'image': None, 'roi':None}

def changePath():

    import sys
    import os

    # change Directory
    os.chdir(os.path.join(os.getcwd(), '../detection_module\\'))
    print(os.getcwd())
    # add to sys path
    sys.path.append(os.getcwd())

def processRoad(vid):
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    queue.put(qInfo)
    p = Process(target=getBgModelAndRoad, args=(vid, queue,))
    p.start()
    p.join()

    return qInfo['image'], qInfo['roi']

def getBgModelAndRoad(vid, queue):
    # changePath()
    import cv2 as cv
    # from Yolov5_DeepSort_Pytorch.track import detect
    from Road_Detection import road
    from Background_subtraction.bg import bg
    import time

    ret = queue.get()
    t1 = time.time()
    IMAGE = bg(vid)  # calling bgSubtract function
    while IMAGE.backgroundFrame is None:
        pass
    t2 = time.time()
    print('Time it took to get a Background Model: %.3fs' % (t2-t1))

    t1 = time.time()
    ROI, IMAGE = road.detect_road(
        IMAGE.backgroundFrame)  # calling road detection function
    t2 = time.time()
    print('Time it took to Extract Road from the Background Model: %.3fs' % (t2-t1))
    # cv.imshow("road", road_surface)
    cv.imwrite("images/road.jpg", IMAGE)
    ret['image'] = IMAGE
    ret['roi'] = ROI
    queue.put(ret)
    

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
