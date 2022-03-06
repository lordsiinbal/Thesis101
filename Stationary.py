
import math
import cv2
import numpy
from tracker import Tracks
import torch
import torchvision.ops.boxes as bops
import torchvision.transforms as T
from PIL import Image
import matplotlib.pyplot as plt
# sys.path.append('deep_sort/deep/reid')
# from torchreid.utils import FeatureExtractor


class Stationary:
    def __init__(self, n_init=4, max_age=300, iou_thresh = 0.7, device = 'cuda'):
        self.tracks = []
        self.next_id = 1
        self._n_init = n_init
        self.max_age = max_age
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.descriptor_extractor = cv2.ORB_create(
            nfeatures=500, edgeThreshold=25, patchSize=25)
        self.iou_thresh = iou_thresh
        self.device = device
        
        # Build transform functions
        pixel_mean=[0.485]
        pixel_std=[0.229]
        transforms = []
        image_size = (128,256)
        transforms += [T.Resize(image_size)]
        transforms += [T.ToTensor()]
        transforms += [T.Normalize(mean=pixel_mean, std=pixel_std)] # normalize pixels
        self.preprocess = T.Compose(transforms)
        self.to_pil = T.ToPILImage()
        self.reverse_preprocess = T.Compose([
            T.ToPILImage(),
            numpy.array,
        ])

    # gets executed every frame
    def update(self, yolo_centroid, xywhs, clss, imc):
        self.height, self.width = imc.shape[:2]
        
        descriptors = self.getDescriptors(
            xywhs, imc, self.descriptor_extractor)  # descriptors of current crops
        currentTracks, outputs, min_dists, tenta = [], [], [], []
        
        if self.isEmptyTracks():  # means empty tracks, no vehicles are being tracked
            self.initDescriptors(descriptors, xywhs, clss)
            return outputs
        
        for i, (t) in enumerate(self.tracks):
            if t.is_deleted():
                self.tracks.pop(i)
            else:
                currentTracks.append(t)
        
        
        for track in currentTracks:  # loop current confirmed tracks
            # calculating the eucdistance for each tracked xy
            xy = self.xyxy_to_xy(track.xyxy)
            distances = [self.distance(xy, pt) for pt in yolo_centroid]
            index_min = numpy.argmin(distances)
         
            if index_min in min_dists or len(min_dists) == len(yolo_centroid):
                # if it already exists, continue to next loop
                track.mark_missed()
                continue
            # now check if the minimum distance's associated descriptor matches the track descriptors
            match_res = self.feature_matcher(track.descriptor, descriptors[index_min])
            if distances[index_min] < track.thresh:
                min_dists.append(index_min)
                if self.get_iou(track.xyxy, self._xywh_to_xyxy(xywhs[index_min])) > self.iou_thresh:
                    if match_res > 0.2:
                        # print(match_res)
                        track.update(self._xywh_to_xyxy(xywhs[index_min]), descriptors[index_min], (
                            xywhs[index_min][2].item(), xywhs[index_min][3].item()), clss[index_min])

                        if track.is_confirmed():
                            outputs.append(numpy.array([track.xyxy[0], track.xyxy[1], track.xyxy[2],
                                                        track.xyxy[3], track.track_id, track.class_id], dtype=numpy.int))
                        continue
            track.mark_missed()
                
        # non-intersecting points from yolo_centroid and min_dists
        if len(min_dists) > 0:
            miss_indeces = numpy.setxor1d(
                [i for i in range(len(descriptors))], min_dists)
            for i in miss_indeces:
                self.tracks.append(Tracks(descriptors[i], self._xywh_to_xyxy(
                    xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age))
                self.next_id += 1

        return outputs

    def _xywh_to_xyxy(self, bbox_xywh=[]):
        x, y, w, h = bbox_xywh
        # if len(wh) > 0:
        #     w, h = wh
        x1 = max(int(x - w / 2), 0)
        x2 = min(int(x + w / 2), self.width - 1)
        y1 = max(int(y - h / 2), 0)
        y2 = min(int(y + h / 2), self.height - 1)
        return x1, y1, x2, y2

    def xyxy_to_xy(self, xyxy):
        x1, y1, x2, y2 = xyxy

        x = ((x1 + x2)/2)
        y = ((y1 + y2)/2)

        return x, y

    def getDescriptors(self, bbox_xywh, ori_img, extractor):
        descriptors = []
        for box in bbox_xywh:
            x1, y1, x2, y2 = self._xywh_to_xyxy(box)
            orig = ori_img[y1:y2, x1:x2]
            #calculate scaling factor
            # scale_factor = (128*128)/(im.shape[0]*im.shape[1])
            # im = cv2.resize(im, None, fx=scale_factor, fy=scale_factor)
            im = cv2.equalizeHist(orig)
            # im = self.preprocessImage(im)
            # cv2.imshow('ss', im)
            _, desc = extractor.detectAndCompute(im, None)
            # imgs = cv2.drawKeypoints(im, _, 0, (0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)    
            # cv2.imshow('a', imgs)
                                                                                                                                                                                            
            # cv2.waitKey()
            
            descriptors.append(desc)
        return descriptors

    def feature_matcher(self, desc_a, desc_b):
        matches = []
        if desc_a is not None and desc_b is not None:
            matches = self.matcher.match(desc_a, desc_b)
            # match_percentage = matches.size(0)/total_matches.size(0) * 100
            mat = [i for i in matches if i.distance < 50]
            
        return 0 if len(matches) == 0 else len(mat)/len(matches)

    def initDescriptors(self, desc, xywhs, clss):
        for i, (desc) in enumerate(desc):
            self.tracks.append(Tracks(desc, self._xywh_to_xyxy(
                xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age))
            self.next_id += 1

    def isEmptyTracks(self):
        return len(self.tracks) == 0

    def get_iou(self, bb1, bb2):
        box1 = torch.tensor([[bb1[0], bb1[1], bb1[2], bb1[3]]], dtype=torch.float).cuda()
        box2 = torch.tensor([[bb2[0], bb2[1], bb2[2], bb2[3]]], dtype=torch.float).cuda()
        iou = bops.box_iou(box1, box2).cuda()
        return iou.item()
    
    def increment_ages(self):
        for t in self.tracks:
            if not t.is_deleted():
                t.mark_missed()
                
    def distance(self, p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def preprocessImage(self, input):
        
        image = self.to_pil(input)
        image = self.preprocess(image)
        images = self.reverse_preprocess(image)
        # images = image.unsqueeze(0).to(self.device)
        # images = numpy.n
        # plt.imshow()
        # cv2.imshow('ss', images)
        # cv2.waitKey()
        return images