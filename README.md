## Inference
To run:
``` bash
python track.py --source eval/data/ --yolo_model yolov5s6.pt --img 640  --deep_sort_model osnet_ain_x0_25 --classes 2 3 5 7 --agnostic-nms --save-vid --conf-thres 0.3 --save-crop
```

## Params description
--yolo_model = 'model.pt path(s)'
--deep_sort_model = 'model.pt path(s)'
--source = source  # file/folder, 0 for webcam
--output = output folder  # output folder
--imgsz, --img, --img-size = inference size h,w
--conf-thres = object confidence threshold
--iou-thres = IOU threshold for NMS
--fourcc = output video codec (verify ffmpeg support)
--device = cuda device, i.e. 0 or 0,1,2,3 or cpu
--show-vid ='display tracking video results
--save-vid ='save video tracking results
--save-txt ='save MOT compliant results to *.txt
--classes ='filter by class: --class 0, or --class 16 17 # class 0 is person, 1 is bycicle, 2 is car... 79 is oven
--agnostic-nms ='class-agnostic NMS
--augment ='augmented inference
--evaluate ='augmented inference
--config_deepsort = default="deep_sort/configs/deep_sort.yaml
--half ="use FP16 half-precision inference
--visualize ='visualize features
--max-det  ='maximum detection per image
--dnn ='use OpenCV DNN for ONNX inference
--project = 'save results to project/name
--name ='save results to project/name
--exist-ok ='existing project/name ok, do not increment
--save-crop ='save cropped

## Cite


```latex
@misc{yolov5deepsort2020,
    title={Real-time multi-object tracker using YOLOv5 and deep sort},
    author={Mikel Broström},
    howpublished = {\url{https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch}},
    year={2020}
}
```
