import sys
import os
from pathlib import Path

PATH = Path(os.path.join(os.getcwd(), '../'))

weights = PATH / 'yolov5/yolov5s.pt'  # model.pt path(s)
# source = ROOT / 'data/images',  # file/dir/URL/glob, 0 for webcam
data = PATH / 'yolov5/data/coco128.yaml'  # dataset.yaml path
imgsz = (360, 640)  # inference size (height, width)
conf_thres = 0.25  # confidence threshold
iou_thres = 0.5 # NMS IOU threshold
max_det = 1000  # maximum detections per image
device = 0  # cuda device, i.e. 0 or 0,1,2,3 or cpu
view_img = True  # show results
save_txt = False  # save results to *.txt
save_conf = False  # save confidences in --save-txt labels
save_crop = True  # save cropped prediction boxes
nosave = False  # do not save images/videos
classes = [2, 3, 5, 7]  # filter by class: --class 0, or --class 0 2 3
agnostic_nms = True  # class-agnostic NMS
augment = False  # augmented inference
visualize = False  # visualize features
update = False  # update all models
project = PATH / 'yolov5/runs/detect'  # save results to project/name
name = 'exp'  # save results to project/name
exist_ok = False  # existing project/name ok, do not increment
line_thickness = 2  # bounding box thickness (pixels)
hide_labels = False  # hide labels
hide_conf = False  # hide confidences
half = False  # use FP16 half-precision inference
dnn = False  # use OpenCV DNN for ONNX inference
