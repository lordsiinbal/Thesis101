
from threading import Thread
import cv2 as cv
import numpy as np
from threading import Thread
    
class bg: 
    def __init__(self, vid):
        cap = cv.VideoCapture(vid)
        frames = []
        FOI = cap.get(cv.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=20) # 20-50 lang dapat kasi may paint naman
        self.backgroundFrame = None
        t = Thread(target=self.sub, args=(cap, FOI, frames))
        t.start()
        
    
    def sub(self, cap, FOI, frames):
        for i,(f) in enumerate(FOI):
            print(i, end='\r')
            cap.set(cv.CAP_PROP_POS_FRAMES, f)
            _, frame = cap.read()
            b = cv.resize(frame,(1280,720), interpolation=cv.INTER_CUBIC)
            frames.append(b)
        self.backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)
        
        
   
