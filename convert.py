# Converts all video files on a directory to mp4

import subprocess
from os import listdir
from os.path import isfile, join
vid_path = "data/drive-download-20220119T020939Z-002aas/CCTV San Felipe/"
onlyfiles = [f for f in listdir(vid_path) if isfile(join(vid_path, f))]
c=1
for i in onlyfiles:
    c=c+1
    i = vid_path+i
    list_dir = subprocess.Popen(["ffmpeg", "-y","-i",i,"-filter:v","fps=30","-c:v","libx264","-crf","24",i[:-4]+".mp4"])
    list_dir.wait()