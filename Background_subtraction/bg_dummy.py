import cv2 as cv
import numpy as np

cap = cv.VideoCapture("vid4.webm")

#for local videos 
FOI = cap.get(cv.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=30)

# #for live videos
# FOI = cap.get()

#creating an array of grames from FOI
frames = []

for frameOI  in FOI:
    cap.set(cv.CAP_PROP_POS_FRAMES, frameOI)
    _, frame = cap.read()
    frames.append(frame)
    
#calculating the average
backgroundFrame = np.median(frames, axis = 0).astype(dtype=np.uint8)

cv.imshow("bg",backgroundFrame)
cv.waitKey()