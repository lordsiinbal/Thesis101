
from threading import Thread
import cv2 as cv
import numpy as np
from threading import Thread
    
class bg: 
    def __init__(self, vid):
        cap = cv.VideoCapture(vid)
        frames = []
        # For local video only
        # FOI = np.random.choice(range(int(cap.get(cv.CAP_PROP_FRAME_COUNT))),size=30, replace= False) # defualt 500
        FOI = cap.get(cv.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=30) # 20-50 lang dapat kasi may paint naman
        self.backgroundFrame = None
        t = Thread(target=self.sub, args=(cap, FOI, frames))
        t.start()
        
    
    def sub(self, cap, FOI, frames):
        for i,(f) in enumerate(FOI):
            print(i, end='\r')
            cap.set(cv.CAP_PROP_POS_FRAMES, f)
            _, frame = cap.read()
            # h, w, __ = frame.shape
            # new_h = int(h/2)
            # new_w = int(w/2) 896,504
            b = cv.resize(frame,(1280,720), interpolation=cv.INTER_CUBIC)
            frames.append(b)
            # #getting the first 1500 frames or 60 seconds, assuming the video is 25 fps
            # if len(frames) == 1500: 
            #     #calculating the average
            #     backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)
            #     break
        self.backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)
        # cv.imwrite("bg.jpg", backgroundFrame)
        
        
   
