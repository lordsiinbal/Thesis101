
import math
import numpy
from tracker import Tracks
from PIL import Image
import imagehash

class Stationary:
    def __init__(self, n_init=4, max_age=300):
        """ n_init = number of consecutive frames a track shoud appear for it to be registerd
            max_age = maximum number of missed misses
        """
        self.tracks = []
        self.next_id = 1
        self._n_init = n_init
        self.max_age = max_age
        
    # gets executed every frame
    def update(self, yolo_centroid, xywhs, clss, imc):
        """yolo_centroid = centroid of detection/yoloboxes
            xywhs = centroid and w and height of yolo
            clss = clases
            imc = current frame
            """
        self.height, self.width = imc.shape[:2]
        
        descriptors = self.getDescriptors(
            xywhs, imc)  # descriptors of current crops
        currentTracks, outputs, min_dists = [], [], []
        
        if self.isEmptyTracks():  # means empty tracks, no vehicles are being tracked
            self.initDescriptors(descriptors, xywhs, clss)
            return outputs
        
        for i, (t) in enumerate(self.tracks):
            if t.is_deleted():
                self.tracks.pop(i)
            else:
                currentTracks.append(t)
        
        for i, (track) in enumerate(currentTracks):  # loop current confirmed tracks
            # calculating the eucdistance for each tracked xy
            xy = self.xyxy_to_xy(track.xyxy)
            distances = [self.distance(xy, pt) for pt in yolo_centroid]
            index_min = numpy.argmin(distances)
         
            if index_min in min_dists or len(min_dists) == len(yolo_centroid):
                # if it already exists, continue to next loop
                track.mark_missed()
                continue
            if distances[index_min] < track.thresh:
                min_dists.append(index_min) 
                match = 1 - (track.descriptor - descriptors[index_min])/64
                if match > 0.7:
                    track.update(self._xywh_to_xyxy(xywhs[index_min]), descriptors[index_min], (
                                xywhs[index_min][2].item(), xywhs[index_min][3].item()), clss[index_min], yolo_centroid[index_min])
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
                #check if there is an exsisting track within the threshold
                xy = self.xyxy_to_xy(self._xywh_to_xyxy(xywhs[i]))
                distances = [self.distance(xy, self.xyxy_to_xy(ct.xyxy)) for ct in currentTracks] # distances with current tracks
            
                index_min = numpy.argmin(distances)
                if distances[index_min] > currentTracks[index_min].thresh: # means outside the thresh of nearest track, meaning new vehicle
                    # new vehicle
                    self.tracks.append(Tracks(descriptors[i], self._xywh_to_xyxy(
                        xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age, (xywhs[i][0].item(), xywhs[i][1].item())))
                    self.next_id += 1
                    continue
                if (xywhs[i][2].item() * xywhs[i][3].item()) > (currentTracks[index_min].wh[0] * currentTracks[index_min].wh[1]):
                    self.tracks.append(Tracks(descriptors[i], self._xywh_to_xyxy(
                        xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age, (xywhs[i][0].item(), xywhs[i][1].item())))
                    self.next_id += 1
                    continue

        return outputs

    def _xywh_to_xyxy(self, bbox_xywh=[]):
        """converts xywh to xyxy"""
        x, y, w, h = bbox_xywh
        x1 = max(int(x - w / 2), 0)
        x2 = min(int(x + w / 2), self.width - 1)
        y1 = max(int(y - h / 2), 0)
        y2 = min(int(y + h / 2), self.height - 1)
        return x1, y1, x2, y2

    def xyxy_to_xy(self, xyxy):
        """converts xyxy to xy center"""
        x1, y1, x2, y2 = xyxy

        x = ((x1 + x2)/2)
        y = ((y1 + y2)/2)

        return x, y

    def getDescriptors(self, bbox_xywh, ori_img):
        """crop detected vehicles and get the pHash for it"""
        descriptors = []
        for box in bbox_xywh:
            x1, y1, x2, y2 = self._xywh_to_xyxy(box)
            im = ori_img[y1:y2, x1:x2]
            im = Image.fromarray(im)
            im = imagehash.phash(im)
            descriptors.append(im)
        return descriptors

    def initDescriptors(self, desc, xywhs, clss):
        """initialize first detection as track, only happens if track is empty"""
        for i, (desc) in enumerate(desc):
            self.tracks.append(Tracks(desc, self._xywh_to_xyxy(
                xywhs[i]), self.next_id, clss[i], self._n_init, (xywhs[i][2].item(), xywhs[i][3].item()), self.max_age, (xywhs[i][0].item(), xywhs[i][1].item())))
            self.next_id += 1

    def isEmptyTracks(self):
        """returns true if track is empty"""
        return len(self.tracks) == 0

    
    def increment_ages(self):
        """increment missed misses of each track"""
        for t in self.tracks:
            if not t.is_deleted():
                t.mark_missed()
                
    def distance(self, p1, p2):
        """euclidean distance formula"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)