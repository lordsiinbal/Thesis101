# limit the number of cpus used by high performance libraries
import os
import sys
import numpy
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

sys.path.insert(0, './yolov5')

from Stationary import Stationary
import json
import datetime
import csv
import argparse
import platform
import shutil
import time
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
from yolov5.models.experimental import attempt_load
from yolov5.utils.downloads import attempt_download
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages, LoadStreams
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator, colors, save_one_box
from yolov5.utils.general import (LOGGER, apply_roi_in_scene, check_img_size, non_max_suppression, scale_coords,
                                  check_imshow, xyxy2xywh, increment_path, isStationary, isInsideROI)


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 deepsort root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


def detect(opt):
    out, source, yolo_model, deep_sort_model, show_vid, save_vid, save_txt, imgsz, evaluate, half, project, name, exist_ok, save_crop = \
        opt.output, opt.source, opt.yolo_model, opt.deep_sort_model, opt.show_vid, opt.save_vid, \
        opt.save_txt, opt.imgsz, opt.evaluate, opt.half, opt.project, opt.name, opt.exist_ok, opt.save_crop
    webcam = source == '0' or source.startswith(
        'rtsp') or source.startswith('http') or source.endswith('.txt')

    # setting up ROI
    file = open('roi.txt', mode='r')
    ROI = file.read()
    file.close()
    ROI = numpy.asarray(json.loads(ROI), dtype=numpy.int32)

    keys = ['id', 'startTime', 'finalTime', 'class',
            'frameStart', 'timeStart', 'isSaved', 'timer']
    vehicleInfos = {k: [] for k in keys}

    device = select_device(opt.device)
    # Initialize
    half &= device.type != 'cpu'  # half precision only supported on CUDA

    # The MOT16 evaluation runs multiple inference streams in parallel, each one writing to
    # its own .txt file. Hence, in that case, the output folder is not restored
    if not evaluate:
        if os.path.exists(out):
            pass
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

    # Directories
    save_dir = increment_path(Path(project) / name,
                              exist_ok=exist_ok)  # increment run
    save_dir.mkdir(parents=True, exist_ok=True)  # make dir

    writer = open(save_dir / 'violations.txt', "w")
    writer.write(str(datetime.datetime.fromtimestamp(
        float(int(time_sync()))).strftime("%m/%d, %I:%M:%S %p"))+'\n')
    writer.write('inference: python track.py --source data/sanfrancisco --yolo_model yolov5s.pt --img 640  --classes 2 3 5 7 --agnostic-nms --save-vid --conf-thres 0.25 --save-crop --show-vid'+'\n')

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(yolo_model, device=device, dnn=opt.dnn)
    stride, names, pt, jit, _ = model.stride, model.names, model.pt, model.jit, model.onnx
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Half
    # half precision only supported by PyTorch on CUDA
    half &= pt and device.type != 'cpu'
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
        dataset = LoadStreams(source, img_size=imgsz,
                              stride=stride, auto=pt and not jit)
        bs = len(dataset)  # batch_size
    else:
        mask = numpy.zeros((720, 1280, 3), numpy.uint8)
        cv2.drawContours(mask, ROI, -1, (255, 255, 255), thickness=-1)
        dataset = LoadImages(source, img_size=imgsz,
                             stride=stride, auto=pt and not jit, mask=mask)
        bs = 1  # batch_size
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names

    # extract what is in between the last '/' and last '.'
    txt_file_name = source.split('/')[-1].split('.')[0]
    txt_path = str(Path(save_dir)) + '/' + txt_file_name + '.txt'

    if pt and device.type != 'cpu':
        model(torch.zeros(
            1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
    dt, seen = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0
    PREV_XY = numpy.zeros([1, 2])
    PREV_XY = numpy.asarray(PREV_XY, dtype=float)
    start_time = time_sync()

    stationary = Stationary(n_init=dataset.fps, max_age=900, match_thresh = 0.7, iou_thresh = 0.5)
    
    for frame_idx, (path, img, im0s, vid_cap, s, fps, tim, frm_id) in enumerate(dataset):
        t1 = time_sync()
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        visualize = increment_path(
            save_dir / Path(path).stem, mkdir=True) if opt.visualize else False
        pred = model(img, augment=opt.augment, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # Apply NMS
        pred = non_max_suppression(
            pred, opt.conf_thres, opt.iou_thres, opt.classes, opt.agnostic_nms, max_det=opt.max_det)
        t00 = time_sync()

        dt[2] += t00 - t3

        # Second-stage classifier (optional)
        # pred = apply_classifier(pred, classifier_model, img, im0s)

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

            imc = im0.copy() if save_crop else im0
            annotator = Annotator(im0, line_width=2, pil=not ascii)

            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                # for c in det[:, -1].unique():
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     # add to string
                #     s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "

                xywhs = xyxy2xywh(det[:, 0:4])
                bbox = det[:, 0:4].cpu().detach().numpy()
                confs = det[:, 4]
                clss = det[:, 5]
                xy = wh = xywhs.cpu().detach().numpy()
                wh = wh[:, 2:]
                xy = xy[:, :2]

                if frame_idx > 0:
                    t6 = time_sync()
                    xy, xywhs, confs, clss, PREV_XY, start_time, PREV_BB = isStationary(xy, wh, xywhs, confs, clss, PREV_XY, fps, frm_id, start_time, bbox, PREV_BB)
                    t7 = time_sync()
                    dt[4] += t7 - t6

                    t11 = time_sync()
                    xy, xywhs, confs, clss = isInsideROI(
                        xy, xywhs, confs, clss, ROI)
                    t12 = time_sync()

                    if len(xy) > 0:
                        t4 = time_sync()
                        # outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), imc) # updating list of tracked stationary vehicles
                        imcc = cv2.cvtColor(imc, cv2.COLOR_BGR2GRAY)
                        # imcc = cv2.GaussianBlur(imcc, (3,3),0)
                        # updating list of tracked stationary vehicles
                      
                        outputs = stationary.update(
                            xy, xywhs.cpu(), clss.cpu(), imcc)

                        t5 = time_sync()
                        dt[3] += t5 - t4
                        # draw boxes for visualization
                        if len(outputs) > 0:
                            for j, (output) in enumerate(outputs) :
                                bboxes = output[0:4]
                                id = output[4]
                                cls = output[5]
                                try:
                                    index = vehicleInfos['id'].index(
                                        id)  # find id in list
                                    c = int(cls)  # integer class
                                    vehicleInfos['class'][index] = names[c]
                                    vehicleInfos['finalTime'][index] = float(
                                        int(time_sync()-vehicleInfos['startTime'][index]))
                                    t = vehicleInfos['timer'][index]/fps
                                    t = str(datetime.timedelta(
                                        seconds=float(t))).split(".")[0]
                                    ts = vehicleInfos['timeStart'][index].split(
                                        ":")
                                    # means 5 mins and not yet saved
                                    if vehicleInfos['timer'][index] >= 300*fps:
                                        col = (0, 0, 255)
                                        if not vehicleInfos['isSaved'][index]:  # save to txt
                                            vehicleInfos['isSaved'][index] = True
                                            startTime = vehicleInfos['timeStart'][index]
                                            # save to csv / txt file here
                                            imgName = save_dir / \
                                                p.name[0:-4] / 'crops' / names[c] / \
                                                f'{id}-{str(ts[0])};{str(ts[1])};{str(ts[2])}.jpg'
                                            # imgName  = f'{id}-{names[c]}.jpg'
                                            data = {
                                                'vehicleID': str(id),
                                                'class': vehicleInfos['class'][index],
                                                'frameStart': vehicleInfos['frameStart'][index],
                                                'timeStart': startTime,
                                                'lengthOfViolation': t,
                                                'imagePath': imgName
                                            }

                                            # saved cropped
                                            save_one_box(
                                                bboxes, imc, file=imgName, BGR=True)
                                            writer.write(str(data)+"\n")
                                            print('saved in violations.txt')
                                    else:
                                        col = (0, 140, 255)
                                    # add 1 to timer (this timer iss within respect of frame)
                                    vehicleInfos['timer'][index] = frm_id - \
                                        vehicleInfos['frameStart'][index]

                                except Exception as er:
                                    vehicleInfos['id'].append(id)
                                    t = time_sync()
                                    vehicleInfos['startTime'].append(t)
                                    vehicleInfos['finalTime'].append(t)
                                    vehicleInfos['frameStart'].append(frm_id)
                                    vehicleInfos['isSaved'].append(False)
                                    vehicleInfos['timer'].append(0)
                                    vehicleInfos['timeStart'].append(
                                        str(datetime.timedelta(seconds=frm_id/fps)).split(".")[0])

                                    t = str(datetime.timedelta(
                                        seconds=float(0))).split(".")[0]
                                    m = 0
                                    c = int(cls)  # integer class
                                    vehicleInfos['class'].append(
                                        names[c])
                                    col = (0, 140, 255)
                                label = f'{id} - {names[c]} | {t}'
                                # label1 = f'{output1[4]} - {names[c]}'
                                annotator.box_label(bboxes, label, color=col)
                                annotator.draw_thresh((output[6],output[7]),(output[10],output[11]), output[8], output[9])
                                
                                # annotator.box_label(bboxes, label1, color=(0,255,0))
                                

                        dt[5] += t5-t1
                        LOGGER.info(
                            f'{s}Done. Read-Frame: ({t1-tim:.3f}s), YOLO:({t3 - t2:.3f}s), NMS:({t00-t3:.3f}s), Tracking:({t5 - t4:.3f}s), isStationary:({t7 - t6:.3f}s), isInsideROI:({t12-t11:.3f}s) Overall:({t5-tim:.3f}s)')
                    else:
                        stationary.increment_ages()
                        LOGGER.info('No detections')       
                else:
                    PREV_BB = bbox
                    PREV_XY = xy 
                    start_time = time.time()
            else:
                stationary.increment_ages()
                LOGGER.info('No detections')

            # Stream results
            im0 = annotator.result()
            im0 = apply_roi_in_scene(ROI, im0)
            if show_vid:
                cv2.imshow(str(p), im0)
                if cv2.waitKey(1) == ord('q'):  # q to quit
                    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
                    res = f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update, %.1fms isStationary, Overall: %.1fms per image at shape {(1, 3, *imgsz)}' % t
                    LOGGER.info(res)
                    writer.write(res)

                    # for i, (ims) in enumerate(imcs):
                    #     cv2.imshow(str(i), ims)
                    # cv2.waitKey()
                    raise StopIteration

            # Save results (image with detections)
            if save_vid:
                if vid_path != save_path:  # new video
                    vid_path = save_path
                    writer.write('\n'+str(vid_path)+'\n')
                    if isinstance(vid_writer, cv2.VideoWriter):
                        vid_writer.release()  # release previous video writer
                    if vid_cap:  # video
                        fps = fps
                        w = int(im0.shape[1])
                        h = int(im0.shape[0])
                    else:  # stream
                        fps, w, h = 30, im0.shape[1], im0.shape[0]
                    keys = ['id', 'startTime', 'finalTime', 'class',
                            'frameStart', 'timeStart', 'isSaved', 'timer']
                    vehicleInfos = {k: [] for k in keys}
                    stationary = Stationary(n_init=dataset.fps, max_age=900, match_thresh = 0.7, iou_thresh = 0.5)# reinitialize stationary tracker
                    vid_writer = cv2.VideoWriter(
                        save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                vid_writer.write(im0)

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    res = f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms deep sort update, %.1fms isStationary, Overall: %.1fms per image at shape {(1, 3, *imgsz)}' % t
    LOGGER.info(res)
    writer.write(res)
    if save_txt or save_vid:
        print('Results saved to %s' % save_path)
        if platform == 'darwin':  # MacOS
            os.system('open ' + save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--yolo_model', nargs='+', type=str,
                        default='yolov5m.pt', help='model.pt path(s)')
    parser.add_argument('--deep_sort_model', type=str, default='osnet_x0_25')
    parser.add_argument('--source', type=str, default='0',
                        help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output',
                        help='output folder')  # output folder
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+',
                        type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float,
                        default=0.3, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float,
                        default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v',
                        help='output video codec (verify ffmpeg support)')
    parser.add_argument('--device', default='',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--show-vid', action='store_true',
                        help='display tracking video results')
    parser.add_argument('--save-vid', action='store_true',
                        help='save video tracking results')
    parser.add_argument('--save-txt', action='store_true',
                        help='save MOT compliant results to *.txt')
    # class 0 is person, 1 is bycicle, 2 is car... 79 is oven
    parser.add_argument('--classes', nargs='+', type=int,
                        help='filter by class: --class 0, or --class 16 17')
    parser.add_argument('--agnostic-nms', action='store_true',
                        help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true',
                        help='augmented inference')
    parser.add_argument('--evaluate', action='store_true',
                        help='augmented inference')
    parser.add_argument("--config_deepsort", type=str,
                        default="deep_sort/configs/deep_sort.yaml")
    parser.add_argument("--half", action="store_true",
                        help="use FP16 half-precision inference")
    parser.add_argument('--visualize', action='store_true',
                        help='visualize features')
    parser.add_argument('--max-det', type=int, default=1000,
                        help='maximum detection per image')
    parser.add_argument('--dnn', action='store_true',
                        help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--project', default=ROOT /
                        'runs/track', help='save results to project/name')
    parser.add_argument('--name', default='exp',
                        help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true',
                        help='existing project/name ok, do not increment')
    parser.add_argument('--save-crop', action='store_true',
                        help='save cropped')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand

    with torch.no_grad():
        detect(opt)
