
import cv2
import numpy
from tracker import Tracks
import torch
import torchvision.ops.boxes as bops
# sys.path.append('deep_sort/deep/reid')
# from torchreid.utils import FeatureExtractor


class Stationary:
    def __init__(self, n_init=4, max_age=300, iou_thresh = 0.7):
        self.tracks = []
        self.next_id = 1
        self._n_init = n_init
        self.max_age = max_age
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.descriptor_extractor = cv2.ORB_create(
            nfeatures=500, edgeThreshold=25, patchSize=25, scoreType=cv2.ORB_FAST_SCORE)
        self.iou_thresh = iou_thresh

    # gets executed every frame
    def update(self, yolo_centroid, xywhs, clss, imc):
        self.height, self.width = imc.shape[:2]
        
        descriptors = self.getDescriptors(
            xywhs, imc, self.descriptor_extractor)  # descriptors of current crops
        currentTracks, outputs, min_dists = [], [], []
        
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
            xdiff = xy[0] - yolo_centroid[:, 0]
            ydiff = xy[1] - yolo_centroid[:, 1]
            distances = numpy.sqrt((xdiff)**2 + (ydiff)**2)
            index_min = numpy.argmin(distances)
         
            if index_min in min_dists or len(min_dists) == len(yolo_centroid):
                # if it already exists, continue to next loop
                track.mark_missed()
                continue
            # now check if the minimum distance's associated descriptor matches the track descriptors
            match_res = self.feature_matcher(track.descriptor, descriptors[index_min])
          
            if distances[index_min] < track.thresh: 
                if self.get_iou(track.xyxy, self._xywh_to_xyxy(xywhs[index_min])) > self.iou_thresh:
                    min_dists.append(index_min)
                    if match_res > 0.65:
                        track.update(self._xywh_to_xyxy(xywhs[index_min]), descriptors[index_min], (
                            xywhs[index_min][2].item(), xywhs[index_min][3].item()), clss[index_min])

                        if track.is_confirmed():
                            outputs.append(numpy.array([track.xyxy[0], track.xyxy[1], track.xyxy[2],
                                                        track.xyxy[3], track.track_id, track.class_id], dtype=numpy.int))
                        continue
                track.mark_missed()
                
        # non-intersecting points from yolo_centroid and min_dists
        miss_indeces = numpy.setxor1d(
            [i for i in range(len(descriptors))], min_dists)
        
        for i in miss_indeces:
            self.tracks.append(Tracks(descriptors[i], self._xywh_to_xyxy(
                xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age))
            self.next_id += 1

        return outputs 

    def _xywh_to_xyxy(self, bbox_xywh=[], wh=[]):
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
            im = ori_img[y1:y2, x1:x2]
            _, desc = extractor.detectAndCompute(im, None)
            descriptors.append(desc)
        return descriptors

    def feature_matcher(self, desc_a, desc_b):
        matches = []
        if desc_a is not None and desc_b is not None:
            matches = self.matcher.match(desc_a, desc_b)
            # match_percentage = matches.size(0)/total_matches.size(0) * 100
            mat = [i for i in matches if i.distance < 45]
            
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