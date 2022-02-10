# limit the number of cpus used by high performance libraries
import os
import threading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.insert(0,'./yolov5')

import argparse
import os
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


class det:
    def __init__(self, opt, source, roi):
        self.frame, self.ret, self.stopped = None, False, False
        out, source, yolo_model, deep_sort_model, show_vid, save_vid, save_txt, imgsz, evaluate, half, project, name, exist_ok= \
            opt.output, source, opt.yolo_model, opt.deep_sort_model, opt.show_vid, opt.save_vid, \
            opt.save_txt, opt.imgsz, opt.evaluate, opt.half, opt.project, opt.name, opt.exist_ok
        webcam = source == '0' or source.startswith(
            'rtsp') or source.startswith('http') or source.endswith('.txt')
        
        MAX_DET = 20
        PREV_XY = np.zeros([1,2])
        PREV_XY = np.asarray(PREV_XY, dtype=int)
        keys = ['id', 'startTime','finalTime', 'class']
        vehicleInfos = {k: [] for k in keys}
        # initialize deepsort
        cfg = get_config()
        cfg.merge_from_file(opt.config_deepsort)
        deepsort = DeepSort(deep_sort_model,
                            max_dist=cfg.DEEPSORT.MAX_DIST,
                            max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                            max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                            use_cuda=True)

        # Initialize
        device = select_device(opt.device)
        half &= device.type != 'cpu'  # half precision only supported on CUDA

        # The MOT16 evaluation runs multiple inference streams in parallel, each one writing to
        # its own .txt file. Hence, in that case, the output folder is not restored
        if not evaluate:
            if os.path.exists(out):
                pass
                shutil.rmtree(out)  # delete output folder
            os.makedirs(out)  # make new output folder

        # Directories
        save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
        save_dir.mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        device = select_device(device)
        model = DetectMultiBackend(yolo_model, device=device, dnn=opt.dnn)
        stride, names, pt, jit, _ = model.stride, model.names, model.pt, model.jit, model.onnx
        imgsz = check_img_size(imgsz, s=stride)  # check image size

        # Half
        half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
        if pt:
            model.model.half() if half else model.model.float()

        # Set Dataloader
        vid_path, vid_writer = None, None
        # Check if environment supports image displays
        if show_vid:
            show_vid = check_imshow()

        # Dataloader
        if webcam:
            show_vid = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
            bs = len(dataset)  # batch_size
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit, roi = roi)
            bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs

        # Get names and colors
        names = model.module.names if hasattr(model, 'module') else model.names

        # extract what is in between the last '/' and last '.'
        txt_file_name = source.split('/')[-1].split('.')[0]
        txt_path = str(Path(save_dir)) + '/' + txt_file_name + '.csv'

        if pt and device.type != 'cpu':
            model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
        dt, seen = [0.0, 0.0, 0.0, 0.0, 0.0], 0
        
        t11 = time_sync()
        self.t = Thread(target=self.detect, args=(imgsz, dataset, device, half, dt, save_dir, opt, model, seen, webcam, names, deepsort, vehicleInfos, save_vid, txt_path, roi, save_txt, t11, show_vid, PREV_XY, vid_path, vid_writer))
        self.flag = True
        self.t.daemon = True
    
    def detect(self, imgsz, dataset, device, half, dt, save_dir, opt, model, seen, webcam, names, deepsort, vehicleInfos, save_vid, txt_path, roi, save_txt, t11, show_vid, PREV_XY, vid_path, vid_writer):
        print("it has started")
        for frame_idx, (path, img, im0s, vid_cap, s, frm_id, vid_fps, video_getter, im, ret) in enumerate(dataset):
            if not self.stopped:
                t1 = time_sync()
                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                t2 = time_sync()
                dt[0] += t2 - t1

                # Inference
                visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if opt.visualize else False
                pred = model(img, augment=opt.augment, visualize=visualize)
                t3 = time_sync()
                dt[1] += t3 - t2

                # Apply NMS
                pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, opt.classes, opt.agnostic_nms, max_det=opt.max_det)
                dt[2] += time_sync() - t3

                # Process detections
                for i, det in enumerate(pred):  # detections per image
                    seen += 1
                    if webcam:  # batch_size >= 1
                        p, im0, _ = path[i], im0s[i].copy(), dataset.count
                        s += f'{i}: '
                    else:
                        p, im0, _ = path, im0s.copy(), getattr(dataset, 'frame', 0)

                    p = Path(p)  # to Path
                    save_path = str(save_dir / p.name)  # im.jpg, vid.mp4, ...
                    s += '%gx%g ' % img.shape[2:]  # print string

                    annotator = Annotator(im, line_width=2, pil=not ascii) # use im image instead of im0

                    if det is not None and len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(
                            img.shape[2:], det[:, :4], im0.shape).round()

                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                        xywhs = xyxy2xywh(det[:, 0:4])
                        confs = det[:, 4]
                        clss = det[:, 5]
                        xy = xywhs.cpu().detach().numpy()
                        xy = xy[:, :2]
                        
                        # Remove vehicles that aren't inside ROI
                        # t6 = time_sync()
                        # xywhs, confs, clss, xy = insideROI(roi, xy, xywhs, confs, clss, det[:, 0:4])
                        # t7 = time_sync()
                        
                        
                        if frm_id != 0: # if on the 0th frame of vid, assume no previous frame
                            
                            # After eliminating vehicles outside ROI, eliminate moving vehicles
                            t8 = time_sync()
                            xywhs, confs, clss, PREV_XY = isStationary(xy, xywhs, confs, clss, PREV_XY, frm_id, vid_fps)
                            t9 = time_sync()
                            # pass detections to deepsort
                            t4 = time_sync()
                            outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), im0)
                            t5 = time_sync()
                            dt[3] += t5 - t4

                            # draw boxes for visualization
                            if len(outputs) > 0:
                                for j, (output, conf) in enumerate(zip(outputs, confs)):
                                    bboxes = output[0:4]
                                    id = output[4]
                                    cls = output[5]
                                    # new ID = new timer, old ID = continue timer check pa si xy previous
                                    try : 
                                        index = vehicleInfos['id'].index(id) # find id in list
                                        c = int(cls)  # integer class
                                        vehicleInfos['class'][index] = names[c]
                                        vehicleInfos['finalTime'][index] = float(int(time_sync()-vehicleInfos['startTime'][index]))
                                        sec = vehicleInfos['finalTime'][index] 
                                        t = str(dtime.timedelta(seconds=sec))
                                        if sec >= 300: # means excedded 5 mins
                                            col = (0,0,255)
                                            #save records here, one time only... 
                                        else:
                                            col = (255,255,0)
                                        label = f'{id} {names[c]}: {t}'
                                        annotator.box_label(bboxes, label, color=col)
                                        
                                    except ValueError:
                                        vehicleInfos['id'].append(id)
                                        t = time_sync()
                                        vehicleInfos['startTime'].append(t)
                                        vehicleInfos['finalTime'].append(t)   

                                        t = str(dtime.timedelta(seconds=float(int(0))))
                                        c = int(cls)  # integer class
                                        vehicleInfos['class'].append(names[c])
                                        label = f'{id} {names[c]}: {t}'
                                        annotator.box_label(bboxes, label, color=(255,255,0))
                        else: # set the prev frame xy to current xy
                            PREV_XY = xy
                        dt[4] += t5 - t1
                        LOGGER.info(f'Done. YOLO:({t3 - t2:.3f}s), DeepSort:({t5 - t4:.3f}s), Stationary:({t9 - t8:.3f}s) Overall:({t5-t1:.3f}s)')

                    else:
                        deepsort.increment_ages()
                        LOGGER.info('No detections')

                    # Stream results
                    im = annotator.result()
                    if show_vid:
                        im = apply_roi_in_scene(roi, im)
                        self.frame, self.ret = im, ret
                        key = cv2.waitKey(1)
                        if key == ord('q'):  # q to quit
                            video_getter.stop()
                            # Print results
                            t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
                            LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update per image at shape {(1, 3, *imgsz)}. \nAverage speed of %.1fms per frame' % t)
                            startTime = []
                            endTime = []
                            for s in vehicleInfos['startTime']:
                                startTime.append(datetime.fromtimestamp(s).strftime("%A, %B %d, %Y %I:%M:%S"))
                            vehicleInfos['startTime'] = startTime
                            for s in vehicleInfos['finalTime']:
                                endTime.append(str(dtime.timedelta(seconds=s)))
                            vehicleInfos['finalTime'] = endTime
                            print(vehicleInfos)
                            
                            if save_txt:
                                # Write MOT compliant results to file
                                with open(txt_path, "w") as outfile:
                                    writer = csv.writer(outfile)
                                    writer.writerow(vehicleInfos.keys())
                                    writer.writerows(zip(*vehicleInfos.values()))
                                    
                            print('MP4 results saved to %s' % save_path)
                            print('CSV results saved to %s' % txt_path)
                            raise StopIteration
                    
                    t0 = time_sync()
                    # Save results (image with detections)
                    if save_vid:
                        now = time.time()
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer
                            if vid_cap:  # video
                                #calculating fps
                                # fps = 19
                                fps = np.ceil((1/(t0-t11))*1.13459)
                                print(fps)
                                # print(vid_fps)
                                w = int(im0.shape[1])
                                h = int(im0.shape[0])
                            else:  # stream
                                fps, w, h = 30, im0.shape[1], im0.shape[0]
                            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                        vid_writer.write(im)
            else:
                video_getter.stop() 
                
    def stop(self):
        self.stopped = True
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

