# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run inference on images, videos, directories, streams, etc.

Usage - sources:
    $ python path/to/detect.py --weights yolov5s.pt --source 0              # webcam
                                                             img.jpg        # image
                                                             vid.mp4        # video
                                                             path/          # directory
                                                             path/*.jpg     # glob
                                                             'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                             'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream

Usage - formats:
    $ python path/to/detect.py --weights yolov5s.pt                 # PyTorch
                                         yolov5s.torchscript        # TorchScript
                                         yolov5s.onnx               # ONNX Runtime or OpenCV DNN with --dnn
                                         yolov5s.xml                # OpenVINO
                                         yolov5s.engine             # TensorRT
                                         yolov5s.mlmodel            # CoreML (MacOS-only)
                                         yolov5s_saved_model        # TensorFlow SavedModel
                                         yolov5s.pb                 # TensorFlow GraphDef
                                         yolov5s.tflite             # TensorFlow Lite
                                         yolov5s_edgetpu.tflite     # TensorFlow Edge TPU
"""

import argparse
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from threading import Thread
from time import time

import cv2
from itsdangerous import json
import numpy
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh, isStationary, isInsideROI, apply_roi_in_scene)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync

sys.path.append('./Tracker/')
from Tracker.tracker import Tracker


from Client.api import baseURL
import requests


@torch.no_grad()
class det:
    """Detection constructor, initializing detection models (yolo and deepsort)\n
        opt = yolo required parameters, can be found and edited at params.py\n
        source = input source/video\n
        roi = road boundary coordinates\n
        shape = input source shape\n
    
    """
    def __init__(self, opt, source, window):
        self.opt = opt
        self.frame, self.ret, self.stopped = None, False, False
        self.vidFrames = []
        self.sfps = 30
        self.start_time = 0
        self.keys = ['id', 'startTime', 'finalTime', 'class', 'frameStart', 'timeStart', 'isSaved', 'timer']
        self.vehicleInfos = {k: [] for k in self.keys}
        source = str(source)
        self.save_img = not self.opt.nosave and not source.endswith('.txt')  # save inference images
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        self.webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
        if is_url and is_file:
            source = check_file(source)  # download

        self.PREV_XY = numpy.zeros([1,2])
        self.PREV_XY = numpy.asarray(self.PREV_XY, dtype=int)

        
        device = select_device(self.opt.device)
        
        # Directories
        self.save_dir = increment_path(Path(opt.project) / self.opt.name, exist_ok=self.opt.exist_ok)  # increment run
        (self.save_dir / 'labels' if self.opt.save_txt else self.save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        self.device = select_device(self.opt.device)
        self.model = DetectMultiBackend(self.opt.weights, device=self.device, dnn=self.opt.dnn, data=self.opt.data)
        stride, self.names, pt, jit, onnx, engine = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx, self.model.engine
        self.imgsz = check_img_size(self.opt.imgsz, s=stride)  # check image size

        # Half
        self.opt.half &= (pt or jit or onnx or engine) and self.device.type != 'cpu'  # FP16 supported on limited backends with CUDA
        if pt or jit:
            self.model.model.half() if self.opt.half else self.model.model.float()

        # Dataloader
        self.view_img = self.opt.view_img
        if self.webcam:
            self.view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(source, img_size=self.imgsz, stride=stride, auto=pt)
            bs = len(self.dataset)  # batch_size
        else:
            # self.mask = numpy.zeros(window.roadImage.shape, numpy.uint8)
            # cv2.drawContours(self.mask, window.ROI, -1, (255,255,255), thickness= -1)
            self.dataset = LoadImages(source, img_size=self.imgsz, stride=stride, auto=pt)
            bs = 1  # batch_size
        self.vid_path, self.vid_writer = [None] * bs, [None] * bs

        # Run inference
        self.model.warmup(imgsz=(1 if pt else bs, 3, *self.imgsz), half=self.opt.half)  # warmup
        self.dt, self.seen = [0.0, 0.0, 0.0, 0.0, 0.0], 0
        
        self.t11 = time_sync()
        self.roi = window.ROI
        self.shape = window.roadImage.shape
        self.t = Thread(target=self.detect, args=()) # use multiprocess instead of thread
        self.flag = False
        self.nflag = True
        self.f = 0
        self.t.daemon = True
        self.window = window
        
    def run(self):
        self.t.start() 
        
        
    def detect(self):
        print("it has started")
        self.flag = True
        tracker = Tracker(n_init=self.dataset.vid_fps, max_age=900, match_thresh=0.7, iou_thresh=0.5)
        if self.window.getViolationRecord:
            violationIDLatest=str(self.window.getViolationRecord[len(self.window.getViolationRecord)-1]['violationID']).split("-")
            violationIDLatest = int(violationIDLatest[1])
        else:
            violationIDLatest = 0
        for frame_idx, (path, img, im0s, vid_cap, s, frm_id, vid_fps, ret, tim) in enumerate(self.dataset):
            if not self.stopped:
                if not self.webcam:
                    self.vid_fps = vid_fps
                    self.frm_id = frm_id
                t1 = time_sync()
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.opt.half else img.float()  # uint8 to fp16/32
                img /= 255  # 0 - 255 to 0.0 - 1.0
                if len(img.shape) == 3:
                    img = img[None]  # expand for batch dim
                t2 = time_sync()
                self.dt[0] += t2 - t1

                # Inference
                self.opt.visualize = increment_path(self.save_dir / Path(path).stem, mkdir=True) if self.opt.visualize else False
                pred = self.model(img, augment=self.opt.augment, visualize=self.opt.visualize)
                t3 = time_sync()
                self.dt[1] += t3 - t2

                # NMS
                pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, self.opt.classes, self.opt.agnostic_nms, max_det=self.opt.max_det)
                self.dt[2] += time_sync() - t3

                # Second-stage classifier (optional)
                # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

                # Process predictions
                for i, det in enumerate(pred):  # per image
                    self.seen += 1
                    if self.webcam:  # batch_size >= 1
                        p, im0, frame = path[i], im0s[i].copy(), self.dataset.count
                        s += f'{i}: '
                        self.frm_id = frm_id = frm_id[i]
                        self.vid_fps = vid_fps = vid_fps[i]
                    else:
                        p, im0, frame = path, im0s.copy(), getattr(self.dataset, 'frame', 0)

                    p = Path(p)  # to Path
                    save_path = str(self.save_dir / p.name)  # im.jpg
                    txt_path = str(self.save_dir / 'labels' / p.stem) + ('' if self.dataset.mode == 'image' else f'_{frame}')  # im.txt
                    s += '%gx%g ' % img.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    imc = im0.copy() if self.opt.save_crop else im0  # for save_crop
                    
                    annotator = Annotator(im0, line_width=self.opt.line_thickness, example=str(self.names))
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                        # Print results
                        # for c in det[:, -1].unique():
                        #     n = (det[:, -1] == c).sum()  # detections per class
                        #     s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                        xywhs = xyxy2xywh(det[:, 0:4])
                        bbox = det[:, 0:4].cpu().detach().numpy()
                        confs = det[:, 4]
                        clss = det[:, 5]
                        xy = wh = xywhs.cpu().detach().numpy()
                        wh = wh[:, 2:]
                        xy = xy[:, :2]
                        
                        if frame_idx > 0:
                            t8 = time_sync()
                            xy, xywhs, confs, clss, self.PREV_XY, self.PREV_BB = isStationary(xy, wh, xywhs, confs, clss, self.PREV_XY, fps, frm_id, bbox, self.PREV_BB)
                            t9 = time_sync()
                            
                            t11 = time_sync()
                            xy, xywhs, confs, clss = isInsideROI(xy, xywhs, confs, clss, self.roi)
                            t12 = time_sync()
                            
                            if len(xy) > 0:
                                t4 = time_sync()
                                outputs = tracker.update(xy, xywhs.cpu(), clss.cpu(), imc)
                                t5 = time_sync()
                                self.dt[3] += t5 - t4
                                
                                # Write results
                                ts = time_sync()
                                if len(outputs) > 0:
                                    for _, (output) in enumerate(outputs):
                                        bboxes = output[0:4]
                                        id = output[4]
                                        cls = output[5]
                                        
                                        # try this block, if it throws an error, means new id
                                        try : 
                                            index = self.vehicleInfos['id'].index(id) # find id in list
                                            c = int(cls)  # integer class
                                            self.vehicleInfos['class'][index] = self.names[c]
                                            self.vehicleInfos['finalTime'][index] = float(int(time_sync()-self.vehicleInfos['startTime'][index]))
                                            
                                            t = self.vehicleInfos['timer'][index]/fps
                                            t = str(timedelta(seconds=float(t))).split(".")[0]
                                            col = (0,165,255)
                                            
                                            if self.vehicleInfos['timer'][index] >= 300*fps: # means 5 mins
                                                col = (0,0,255)
                                                if not self.vehicleInfos['isSaved'][index]: # if not yet saved
                                                    #determining if the dataRoadViolation is empty
                                                    violationIDLatest +=1
                                                    violationID="V-" + str(violationIDLatest).zfill(7)
                                                    
                                                    imgName = self.save_dir / p.name[0:-4]  / 'crops' / self.names[c] / f'{id}.jpg'   
                                                    # save violation here
                                                    #making the data a json type
                                                    data = {
                                                                    'violationID' :  violationID,
                                                                    'vehicleID' : str(id),
                                                                    'roadName' : self.window.window.label.text(),
                                                                    'roadID' : self.window.roadIDGlobal,
                                                                    'lengthOfViolation' :  t,
                                                                    'startDateAndTime' :str(datetime.fromtimestamp(self.vehicleInfos['startTime'][index]).strftime("%m/%d%Y, %I:%M:%S %p")),
                                                                    'endDateAndTime' : str(datetime.fromtimestamp(float(int(time_sync()))).strftime("%m/%d%Y, %I:%M:%S %p")),
                                                                    'frameStart' : str(self.vehicleInfos['frameStart'][index]),
                                                                    'violationRecord' : str(self.save_dir / p.name), # filepath of video
                                                                    'vehicleClass' : str(self.names[c]) 
                                                                    
                                                    }
                                                    save_one_box(bboxes, imc, file = imgName, BGR=True) # saved cropped
                                                    self.saveViolation(data) #calling the saveViolation Function to save the data to the database
                                                    self.vehicleInfos['isSaved'][index] = True
                                                    
                                            label = f'{id} {self.names[c]}: {t}'
                                            annotator.box_label(bboxes, label, color=col)
                                            self.vehicleInfos['timer'][index] = frm_id - self.vehicleInfos['frameStart'][index]
                                            
                                        except ValueError:
                                            self.vehicleInfos['id'].append(id)
                                            t = time_sync()
                                            self.vehicleInfos['startTime'].append(t)
                                            self.vehicleInfos['finalTime'].append(t)
                                            self.vehicleInfos['frameStart'].append(frm_id)
                                            self.vehicleInfos['isSaved'].append(False)
                                            self.vehicleInfos['timer'].append(0)
                                            self.vehicleInfos['timeStart'].append(str(timedelta(seconds=frm_id/fps)))
                                            t = str(timedelta(seconds=float(int(0)))).split(".")[0]
                                            c = int(cls)  # integer class
                                            self.vehicleInfos['class'].append(self.names[c])
                                            label = f'{id} {self.names[c]}'
                                            annotator.box_label(bboxes, label, color=(0,165,255))
                                tss = time_sync()
                                self.dt[4] += t5 - tim
                                # LOGGER.info(f'Done. Read-frame: ({t1-tim:.3f}), YOLO:({t3 - t2:.3f}s), Tracker:({t5 - t4:.3f}s), Stationary:({t9 - t8:.3f}s), isInsideROI: ({t12-t11:.3f}s) Overall:({t5-tim:.3f}s)')
                        else:
                            self.PREV_BB = bbox
                            self.PREV_XY = xy 
                    else:
                        tracker.increment_ages()
                        LOGGER.info('No detections')
                    # Stream results
                    im0 = annotator.result()
                    im0 = apply_roi_in_scene(self.roi, im0)
                    if self.view_img:
                        self.frame, self.ret = im0, ret
                    self.f = frame_idx
                    # Save results (image with detections)
                    if self.save_img:
                        if self.dataset.mode == 'image':
                            cv2.imwrite(save_path, im0)
                        else:  # 'video' or 'stream'
                            if self.vid_path[i] != save_path:  # new video
                                self.vid_path[i] = save_path
                                if isinstance(self.vid_writer, cv2.VideoWriter):
                                    self.vid_writer.release()  # release previous video writer
                                if vid_cap:  # video
                                    fps = vid_cap.get(cv2.CAP_PROP_FPS)
                                    w = int(im0.shape[1])
                                    h = int(im0.shape[0])
                                else:  # stream
                                    fps, w, h = 30, im0.shape[1], im0.shape[0]
                                save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                                self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                                self.keys = ['id', 'startTime', 'finalTime', 'class', 'frameStart', 'timeStart', 'isSaved', 'timer']
                                self.vehicleInfos = {k: [] for k in self.keys}
                                tracker = Tracker(n_init=self.dataset.vid_fps, max_age=900, match_thresh=0.7, iou_thresh=0.5)
                            self.vid_writer.write(im0)
                            self.vidFrames.append(im0)
                
            else:
                self.vid_writer.release() #stop from writing video
                t = tuple(x / self.seen * 1E3 for x in self.dt)  # speeds per image
                LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update per image at shape {(1, 3, *self.imgsz)}. \nAverage speed of %.1fms per detection' % t)
                raise StopIteration 
    
        # if done   
        # Print results
        t = tuple(x / self.seen * 1E3 for x in self.dt)  # speeds per image
        LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *self.opt.imgsz)}' % t)
        if self.opt.save_txt or self.save_img:
            s = f"\n{len(list(self.save_dir.glob('labels/*.txt')))} labels saved to {self.save_dir / 'labels'}" if self.opt.save_txt else ''
            LOGGER.info(f"Results saved to {colorstr('bold', self.save_dir)}{s}")
        if self.opt.update:
            strip_optimizer(self.opt.weights)  # update model (to fix SourceChangeWarning)

    def stop(self):
        self.stopped = True
    
    def saveViolation(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        # print(data)
        r = requests.post(url = baseURL + "/ViolationInsert",data=json.dumps(data),headers=headers)
        # print(r)


    def changeROI(self, ROI):
        self.roi = ROI
        # self.mask = numpy.zeros(self.shape, numpy.uint8)
        # cv2.drawContours(self.mask, self.roi, -1, (255,255,255), thickness= -1)
        # self.dataset.mask = self.mask