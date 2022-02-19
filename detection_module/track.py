# limit the number of cpus used by high performance libraries
import json
from queue import Queue
import threading
import os
from flask import request
import multiprocessing
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.insert(0,'./yolov5')

import argparse

import platform
import shutil
import time
import numpy as np
from pathlib import Path
import cv2
import torch
import datetime as dtime
import torch.backends.cudnn as cudnn
import csv

from multiprocessing import Process
from threading import Thread
from datetime import datetime
from yolov5.models.experimental import attempt_load
from yolov5.utils.downloads import attempt_download
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages, LoadStreams
from yolov5.utils.general import (LOGGER, check_img_size, non_max_suppression, scale_coords, 
                                  check_imshow, xyxy2xywh, increment_path, apply_roi_in_scene, isStationary)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator

from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort

from records.dbProcess import save, read
from Client.api import baseURL
import requests
from Client.mainUi import TableUi



class det:
    """Detection constructor, initializing detection models (yolo and deepsort)\n
        opt = yolo required parameters, can be found and edited at params.py\n
        source = input source/video\n
        roi = road boundary coordinates\n
        shape = input source shape\n
    
    """
    def __init__(self, opt, source, roi, shape):
        self.frame, self.ret, self.stopped = None, False, False
        self.vidFrames = []
        self.sfps = 30
        # self.violationKeys = ['violationID', 'vehicleID','roadName', 'lengthOfViolation','startDateAndTime', 'endDateAndTime']
        self.keys = ['id', 'startTime','finalTime', 'class']
        self.vehicleInfos = {k: [] for k in self.keys}
        # self.violationInfos = {k: [] for k in self.violationKeys}
        self.out, self.source, self.yolo_model, self.deep_sort_model, self.show_vid, self.save_vid, self.save_txt, self.imgsz, self.evaluate, self.half, self.project, self.name, self.exist_ok= \
            opt.output, source, opt.yolo_model, opt.deep_sort_model, opt.show_vid, opt.save_vid, \
            opt.save_txt, opt.imgsz, opt.evaluate, opt.half, opt.project, opt.name, opt.exist_ok
        self.webcam = self.source == '0' or self.source.startswith(
            'rtsp') or self.source.startswith('http') or self.source.endswith('.txt')
        
        self.MAX_DET = 20
        self.PREV_XY = np.zeros([1,2])
        self.PREV_XY = np.asarray(self.PREV_XY, dtype=int)
       
        # initialize deepsort
        self.cfg = get_config()
        self.cfg.merge_from_file(opt.config_deepsort)
        self.deepsort = DeepSort(self.deep_sort_model,
                            max_dist=self.cfg.DEEPSORT.MAX_DIST,
                            max_iou_distance=self.cfg.DEEPSORT.MAX_IOU_DISTANCE,
                            max_age=self.cfg.DEEPSORT.MAX_AGE, n_init=self.cfg.DEEPSORT.N_INIT, nn_budget=self.cfg.DEEPSORT.NN_BUDGET,
                            use_cuda=True)

        # Initialize
        self.device = select_device(opt.device)
        self.half &= self.device.type != 'cpu'  # half precision only supported on CUDA

        # The MOT16 evaluation runs multiple inference streams in parallel, each one writing to
        # its own .txt file. Hence, in that case, the output folder is not restored
        if not self.evaluate:
            if os.path.exists(self.out):
                pass
                shutil.rmtree(self.out)  # delete output folder
            os.makedirs(self.out)  # make new output folder

        # Directories
        self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)  # increment run
        self.save_dir.mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        self.device = select_device(self.device)
        self.model = DetectMultiBackend(self.yolo_model, device=self.device, dnn=opt.dnn)
        stride, self.names, pt, jit, _ = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx
        self.imgsz = check_img_size(self.imgsz, s=stride)  # check image size

        # Half
        self.half &= pt and self.device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
        if pt:
            self.model.model.half() if self.half else self.model.model.float()

        # Set Dataloader
        self.vid_path, self.vid_writer = None, None
        # Check if environment supports image displays
        if self.show_vid:
            self.show_vid = check_imshow()

        # Dataloader
        if self.webcam:
            self.show_vid = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(self.source, img_size=self.imgsz, stride=stride, auto=pt and not jit)
            bs = len(self.dataset)  # batch_size
        else:
            # getting the mask of roi
            self.mask = np.zeros(shape, np.uint8)
            cv2.drawContours(self.mask, roi, -1, (255,255,255), thickness= -1)
            self.dataset = LoadImages(self.source, img_size=self.imgsz, stride=stride, auto=pt and not jit, mask = self.mask)
            bs = 1  # batch_size
        self.vid_path, self.vid_writer = [None] * bs, [None] * bs

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names

        # extract what is in between the last '/' and last '.'
        txt_file_name = source.split('/')[-1].split('.')[0]
        self.txt_path = str(Path(self.save_dir)) + '/' + txt_file_name + '.csv'

        if pt and self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, *self.imgsz).to(self.device).type_as(next(self.model.model.parameters())))  # warmup
        self.dt, self.seen = [0.0, 0.0, 0.0, 0.0, 0.0], 0
        
        self.t11 = time_sync()
        self.opt = opt
        self.roi = roi
        self.shape = shape
        self.num_processes = multiprocessing.cpu_count()
        self.t = Thread(target=self.detect, args=()) # use multiprocess instead of thread
        self.flag = False
        self.nflag = True
        self.f = 0
        self.t.daemon = True
    
    
    def run(self):
        self.dataset.begin()
        self.t.start()
    
    """detection function"""
    def detect(self):
        print("it has started")
        self.flag = True
        for frame_idx, (path, img, im0s, vid_cap, s, frm_id, vid_fps, video_getter, im, ret, tim) in enumerate(self.dataset):
            if not self.stopped:
                self.vid_fps = vid_fps
                self.frm_id = frm_id
                t1 = time_sync()
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                t2 = time_sync()
                self.dt[0] += t2 - t1

                # Inference
                visualize = increment_path(self.save_dir / Path(path).stem, mkdir=True) if self.opt.visualize else False
                pred = self.model(img, augment=self.opt.augment, visualize=visualize)
                t3 = time_sync()
                self.dt[1] += t3 - t2

                # Apply NMS
                pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, self.opt.classes, self.opt.agnostic_nms, max_det=self.opt.max_det)
                self.dt[2] += time_sync() - t3

                # Process detections
                for i, det in enumerate(pred):  # detections per image
                    self.seen += 1
                    if self.webcam:  # batch_size >= 1
                        p, im0, _ = path[i], im0s[i].copy(), self.dataset.count
                        s += f'{i}: '
                    else:
                        p, im, _ = path, im.copy(), getattr(self.dataset, 'frame', 0)

                    p = Path(p)  # to Path
                    save_path = str(self.save_dir / p.name)  # im.jpg, vid.mp4, ...
                    s += '%gx%g ' % img.shape[2:]  # print string

                    
                    annotator = Annotator(im, line_width=2, pil=not ascii)

                    if det is not None and len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(
                            img.shape[2:], det[:, :4], im.shape).round()

                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                        xywhs = xyxy2xywh(det[:, 0:4])
                        confs = det[:, 4]
                        clss = det[:, 5]
                        xy = xywhs.cpu().detach().numpy()
                        xy = xy[:, :2]

                        if frm_id != 0: # if on the 0th frame of vid, assume no previous frame
                            
                            # After eliminating vehicles outside ROI, eliminate moving vehicles
                            t8 = time_sync()
                            xywhs, confs, clss, self.PREV_XY = isStationary(xy, xywhs, confs, clss, self.PREV_XY, frm_id, vid_fps)
                            t9 = time_sync()
                            # pass detections to deepsort
                            t4 = time_sync()
                            outputs = self.deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), im)
                            t5 = time_sync()
                            self.dt[3] += t5 - t4

                            # im0 = cropped frame
                            # im = full frame
                            
                            # draw boxes for visualization
                            if len(outputs) > 0:
                                for j, (output, conf) in enumerate(zip(outputs, confs)):
                                    bboxes = output[0:4]
                                    id = output[4]
                                    cls = output[5]
                                    # new ID = new timer, old ID = continue timer check pa si xy previous
                                    try : 
                                        index = self.vehicleInfos['id'].index(id) # find id in list
                                        c = int(cls)  # integer class
                                        self.vehicleInfos['class'][index] = self.names[c]
                                        self.vehicleInfos['finalTime'][index] = float(int(time_sync()-self.vehicleInfos['startTime'][index]))
                                        sec = self.vehicleInfos['finalTime'][index] 
                                        t = str(dtime.timedelta(seconds=sec))
                                        if sec == 300: # means 5 mins
                                            col = (0,0,255)
                                            
                                            # if TableUi.dataViolationGlobal: #determining if the dataRoadGlobal is empty
                                            #     roadIDLatest=str(self.road.dataRoadGlobal[len(self.road.dataRoadGlobal)-1]['roadID']).split("-")
                                            #     print(roadIDLatest)
                                            #     intRoadID=int(roadIDLatest[1]) + 1
                                            #     roadID="R-" + str(intRoadID).zfill(7)
                                            #     print(roadID)
                                                
                                            # else:
                                            #     type = 'road'
                                            #     roadID = "R-000000"+str(read(type)+1)


                                            # save violation here
                                            #making the data a json type
                                            data = {
                                                            'violationID' : str(read('violation')+1),
                                                            'vehicleID' : str(id),
                                                            'roadName' : "San Felipe",
                                                            'lengthOfViolation' : str(dtime.timedelta(seconds=sec)),
                                                            'startDateAndTime' :datetime.fromtimestamp(self.vehicleInfos['startTime'][index]).strftime("%A, %B %d, %Y %I:%M:%S"),
                                                            'endDateAndTime' : datetime.fromtimestamp(float(int(time_sync()))).strftime("%A, %B %d, %Y %I:%M:%S")
                                                        }
                                            self.saveViolation(data) #calling the saveViolation Function to save the data to the database
                                        elif sec > 300: #exceed 5 mins
                                            col = (0,0,255)
                                        else:
                                            col = (0,165,255)
                                        label = f'{id} {self.names[c]}: {t}'
                                        annotator.box_label(bboxes, label, color=col)
                                        
                                    except ValueError:
                                        self.vehicleInfos['id'].append(id)
                                        t = time_sync()
                                        self.vehicleInfos['startTime'].append(t)
                                        self.vehicleInfos['finalTime'].append(t)   

                                        t = str(dtime.timedelta(seconds=float(int(0))))
                                        c = int(cls)  # integer class
                                        self.vehicleInfos['class'].append(self.names[c])
                                        label = f'{id} {self.names[c]}: {t}'
                                        annotator.box_label(bboxes, label, color=(0,165,255))
                        else: # set the prev frame xy to current xy
                            self.PREV_XY = xy
                        self.dt[4] += t5 - tim
                        LOGGER.info(f'Done. Read-frame: ({t1-tim:.3f}), YOLO:({t3 - t2:.3f}s), DeepSort:({t5 - t4:.3f}s), Stationary:({t9 - t8:.3f}s) Overall:({t5-tim:.3f}s)')

                    else:
                        self.deepsort.increment_ages()
                        LOGGER.info(f'Done. Read-frame: ({t1-tim:.3f}) YOLO:({t3 - t2:.3f}s) No detections ')

                    # Stream results
                    im = annotator.result()
                    im = apply_roi_in_scene(self.roi, im)
                    if self.show_vid:
                        self.frame, self.ret = im, ret
                        # saving only when quitted
                        # if key == ord('q'):  # q to quit
                        #     video_getter.stop()
                            # Print results
                            # startTime = []
                            # endTime = []
                            # for s in self.vehicleInfos['startTime']:
                            #     startTime.append(datetime.fromtimestamp(s).strftime("%A, %B %d, %Y %I:%M:%S"))
                            # self.vehicleInfos['startTime'] = startTime
                            # for s in self.vehicleInfos['finalTime']:
                            #     endTime.append(str(dtime.timedelta(seconds=s)))
                            # self.vehicleInfos['finalTime'] = endTime
                            # print(self.vehicleInfos)
                            
                            # if self.save_txt:
                            #     # Write MOT compliant results to file
                            #     with open(self.txt_path, "w") as outfile:
                            #         writer = csv.writer(outfile)
                            #         writer.writerow(self.vehicleInfos.keys())
                            #         writer.writerows(zip(*self.vehicleInfos.values()))
                                    
                            # print('MP4 results saved to %s' % save_path)
                            # print('CSV results saved to %s' % self.txt_path)
                    self.f = frame_idx
                    
                    t0 = time_sync()
                    # Save results (image with detections)
                    if self.save_vid:
                        now = time.time()
                        if self.vid_path != save_path:  # new video
                            self.vid_path = save_path
                            if isinstance(self.vid_writer, cv2.VideoWriter):
                                self.vid_writer.release()  # release previous video writer
                            if vid_cap:  # video
                                #calculating fps
                                # fps = 19
                                self.sfps = np.ceil((1/(t0-self.t11))*1.5)
                                
                                # print(vid_fps)
                                w = int(im.shape[1])
                                h = int(im.shape[0])
                                print( self.sfps, w, h)
                            else:  # stream
                                 self.sfps, w, h = 30, im.shape[1], im.shape[0]
                            self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'),  self.sfps, (w, h))
                        self.vid_writer.write(im)
                        self.vidFrames.append(im)
                    
            else:
                video_getter.stop() 
                t = tuple(x / self.seen * 1E3 for x in self.dt)  # speeds per image
                LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update per image at shape {(1, 3, *self.imgsz)}. \nAverage speed of %.1fms per frame' % t)
                raise StopIteration        
                
    def stop(self):
        self.stopped = True
    
    def saveViolation(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        print("violation 1")
        print(data)
        r = requests.post(url = baseURL + "/ViolationInsert",data=json.dumps(data),headers=headers)
        print(r)


    def changeROI(self, ROI):
        self.roi = ROI
        self.mask = np.zeros(self.shape, np.uint8)
        cv2.drawContours(self.mask, self.roi, -1, (255,255,255), thickness= -1)
        self.dataset.mask = self.mask
    # # Print results
    # t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    # LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update \
    #     per image at shape {(1, 3, *imgsz)}. Average speed of %.1fms per frame' % t )
    
    # if save_txt or save_vid:
    #     startTime = []
    #     endTime = []
    #     for s in vehicleInfos['startTime']:
    #         startTime.append(datetime.fromtimestamp(s).strftime("%A, %B %d, %Y %I:%M:%S"))
    #     vehicleInfos['startTime'] = startTime
    #     for s in vehicleInfos['finalTime']:
    #         endTime.append(str(dtime.timedelta(seconds=s)))
    #     vehicleInfos['finalTime'] = endTime
    #     print('Results saved to %s' % save_path)
    #     if platform == 'darwin':  # MacOS
    #         os.system('open ' + save_path)

