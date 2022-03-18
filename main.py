

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
    qInfo = {'image': None, 'roi':None, 'k_size':None}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    queue.put(qInfo)
    p = Process(target=getBgModelAndRoad, args=(vid, queue, p,))
    p.start()
    p.join()
    qInfo = queue.get()
    return qInfo['image'], qInfo['roi'], qInfo['k_size']

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
    ROI, IMAGE, K_SIZE = road.detect_road(
        IMAGE.backgroundFrame)  # calling road detection function
    t2 = time.time()
    print('Time it took to Extract Road from the Background Model: %.3fs' % (t2-t1))

    cv.imwrite(p+"/images/road.jpg", bgM)
    ret['image'] = IMAGE
    ret['roi'] = ROI
    ret['k_size'] = K_SIZE
    
    queue.put(ret)
    

class detection:
    def __init__(self, vid, window):
        # changePath()
        sys.path.append('/yolov5/')
        from yolov5.detect import det
        import params
        import torch
        import numpy as np
        import cv2
        
        min_size = int(window.roadImage.shape[0]*window.roadImage.shape[1]*0.05)
        contours = window.ROI
        bg = np.zeros_like(window.roadImage)  
        for contour in contours:
            area = cv2.contourArea(contour) 
            print(f'area {area} < {min_size*0.5} : {area<min_size*0.5}')
            if area < min_size:
                continue
            cv2.drawContours(bg, [contour], -1, (255,255,255), thickness= -1)

        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        kernel  = np.ones((window.k_size,window.k_size), np.uint8)
        dilated = cv2.dilate(bg, kernel, iterations=1)
        
        # pass 1
        smooth_mask_blurred   = cv2.GaussianBlur(dilated, (21,21), 0)
        _, smooth_mask_threshed1  = cv2.threshold(smooth_mask_blurred, 128, 255, cv2.THRESH_BINARY)
        
        # pass 2
        smooth_mask_blurred   = cv2.GaussianBlur(smooth_mask_threshed1, (21,21), 0)
        _, smooth_mask_threshed2 =  cv2.threshold(smooth_mask_blurred, 128, 255, cv2.THRESH_BINARY)
        
        cnts, _ = cv2.findContours(smooth_mask_threshed2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        window.ROI = cnts
        
        # params.imgsz *= 2 if len(params.imgsz) == 1 else 1  # expand
        with torch.no_grad():
            # calling the yolov5 and deepsort module
            # initializing the detection
            self.dets = det(params, source=vid, window = window)
# NOTE: APPLY THE ROI, REUTRN THE COORDINATES OF THE WHOLE CONTOURS #DONE----------
