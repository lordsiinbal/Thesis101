
from threading import Thread
import cv2 as cv
import cv2
import numpy as np
from threading import Thread
    
class bg: 
    def __init__(self, vid):
        vid = str(vid)
        is_url = vid.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        cap = cv.VideoCapture(vid)
        size = 20
        FOI = cap.get(cv.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=size) 
        self.backgroundFrame = None
        if not is_url:
            t = Thread(target=self.sub, args=(cap, FOI))
        else:
            t = Thread(target=self.subLive, args=(cap, size))
        t.start()
        
    
    def sub(self, cap, FOI):
        print('not live')
        frames = []
        for i,(f) in enumerate(FOI):
            print(i, end='\r')
            cap.set(cv.CAP_PROP_POS_FRAMES, f)
            _, frame = cap.read()
            b = cv.resize(frame,(1280,720), interpolation=cv.INTER_CUBIC)
            frames.append(b)
        self.backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)
        
    def subLive(self, cap, size):
        i = 0
        frames = []
        while(cap.isOpened()):
            print(i, end='\r')
            ret, frame = cap.read()
            if ret:
                b = cv.resize(frame,(1280,720), interpolation=cv.INTER_CUBIC)
                frames.append(b)
            if(i==size):
                self.backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)
                break
            i+=1
        
        
        
   
