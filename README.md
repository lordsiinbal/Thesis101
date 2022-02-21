## Inference
To run:
``` bash
python track.py --source eval/data/ --yolo_model yolov5s6.pt --img 640  --deep_sort_model osnet_ain_x0_25 --classes 2 3 5 7 --agnostic-nms --save-vid --conf-thres 0.3 --save-crop
```

## Params description
--yolo_model = 'model.pt path(s)'\n
--deep_sort_model = 'model.pt path(s)'\n
--source = source  # file/folder, 0 for webcam\n
--output = output folder  # output folder\n
--imgsz, --img, --img-size = inference size h,w\n
--conf-thres = object confidence threshold\n
--iou-thres = IOU threshold for NMS\n
--fourcc = output video codec (verify ffmpeg support)\n
--device = cuda device, i.e. 0 or 0,1,2,3 or cpu\n
--show-vid ='display tracking video results\n
--save-vid ='save video tracking results\n
--save-txt ='save MOT compliant results to *.txt\n
--classes ='filter by class: --class 0, or --class 16 17 # class 0 is person, 1 is bycicle, 2 is car... 79 is oven
--agnostic-nms ='class-agnostic NMS\n
--augment ='augmented inference\n
--evaluate ='augmented inference\n
--config_deepsort = default="deep_sort/configs/deep_sort.yaml\n
--half ="use FP16 half-precision inference\n
--visualize ='visualize features\n
--max-det  ='maximum detection per image\n
--dnn ='use OpenCV DNN for ONNX inference\n
--project = 'save results to project/name\n
--name ='save results to project/name\n
--exist-ok ='existing project/name ok, do not increment\n
--save-crop ='save cropped\n

## Cite


```latex
@misc{yolov5deepsort2020,
    title={Real-time multi-object tracker using YOLOv5 and deep sort},
    author={Mikel Broström},
    howpublished = {\url{https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch}},
    year={2020}
}
```
