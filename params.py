import sys
import os
from pathlib import Path

# model.pt path(s) choose between yolov5m, yolov5n6, yolov5m6, yolov5x

yolo_model='yolov5n6.pt'
deep_sort_model='osnet_x0_25'
output='inference/output'
imgsz=[720]
conf_thres=0.4
iou_thres=0.5
fourcc='mp4v'
device=0
save_vid = True
evaluate=False
config_deepsort="deep_sort/configs/deep_sort.yaml"
half=True
max_det = 1000  # maximum detections per image
show_vid = True  # show results
save_txt = True  # save results to *.txt
save_conf = False  # save confidences in --save-txt labels
save_crop = False  # save cropped prediction boxes
nosave = False  # do not save images/videos
classes = [2, 3, 5, 7]  # filter by class: --class 0, or --class 0 2 3
agnostic_nms = True  # class-agnostic NMS
augment = False  # augmented inference
visualize = False  # visualize features
update = False  # update all models
project = 'runs/detect'  # save results to project/name
name = 'exp'  # save results to project/name
exist_ok = False  # existing project/name ok, do not increment
line_thickness = 1  # bounding box thickness (pixels)
hide_labels = False  # hide labels
hide_conf = True  # hide confidences
dnn = False  # use OpenCV DNN for ONNX inference

