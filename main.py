

from multiprocessing import Process, Queue
import multiprocessing
import sys
from threading import Thread
from typing import Iterable
from winreg import QueryInfoKey


# IMAGE, ROI = None, None
def changePath():

    import sys
    import os

    # change Directory
    os.chdir(os.path.join(os.getcwd(), '../yolov5\\'))
    print(os.getcwd())
    # add to sys path
    sys.path.append(os.getcwd())

def processRoad(vid, p):
    qInfo = {'image': None, 'roi':None}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    queue.put(qInfo)
    p = Process(target=getBgModelAndRoad, args=(vid, queue, p,))
    p.start()
    p.join()
    qInfo = queue.get()
    return qInfo['image'], qInfo['roi']

def getBgModelAndRoad(vid, queue, p):
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
    bgM = IMAGE.backgroundFrame

    t1 = time.time()
    ROI, IMAGE = road.detect_road(
        IMAGE.backgroundFrame)  # calling road detection function
    t2 = time.time()
    print('Time it took to Extract Road from the Background Model: %.3fs' % (t2-t1))

    cv.imwrite(p+"/images/road.jpg", bgM)
    ret['image'] = IMAGE
    ret['roi'] = ROI
    
    queue.put(ret)
    

class detection:
    def __init__(self, vid, window):
        # changePath()
        sys.path.append('/yolov5/')
        from yolov5.detect import det
        import params
        import torch
        
        # params.imgsz *= 2 if len(params.imgsz) == 1 else 1  # expand
        with torch.no_grad():
            # calling the yolov5 and deepsort module
            # initializing the detection
            self.dets = det(params, source=vid, window = window)
# NOTE: APPLY THE ROI, REUTRN THE COORDINATES OF THE WHOLE CONTOURS #DONE----------
