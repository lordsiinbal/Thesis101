
import numpy
class TrackState:

    Tentative = 1  # tracks registration stage stage, initialized but not confirmed
    Confirmed = 2  # Confirmed tracks, tracks that is done in n_init and registraion
    Deleted = 3  # removed tracks


class Tracks:
    def __init__(self, descriptor, xyxy, id, class_id, n_init, wh, max_age):
        self.track_id = id
        self.xyxy = xyxy
        self.class_id = class_id
        self.n_init = n_init
        self.track_state = TrackState.Tentative
        self.calls = 0
        self.wh = wh
        self.descriptor = descriptor
        self.last_seen = 0
        self.max_age = max_age
        self.missed = False
        self.thresh = self.computeEucDist(xyxy, self.wh)

    def computeEucDist(self, xyxy, wh):
        x1, y1, x2, y2 = xyxy

        x = (x1 + x2)/2
        y = (y1 + y2)/2

        a = wh[0] * wh[1] * 0.002
        xy = numpy.array((x, y))
        u = numpy.array((x+a, y+a))

        dist = numpy.sqrt(((u[0]-xy[0])**2)+((u[1]-xy[1])**2))

        return dist

    def update(self, xyxy, descriptor, wh, class_id):
        if self.calls == self.n_init:
            self.track_state = TrackState.Confirmed
            print(f'vehicle id = {self.track_id} has been registered')
            self.descriptor = descriptor
            # calculate thresh
            self.xyxy = xyxy
        elif self.calls < self.n_init:
            self.descriptor = descriptor
            self.xyxy = xyxy
        if self.track_state == TrackState.Confirmed:
            self.xyxy = xyxy

        self.thresh = self.computeEucDist(xyxy, wh)
        self.last_seen = 0
        self.calls += 1
        self.missed = False
        self.class_id = class_id

    def mark_missed(self):
        """Mark this track as missed (no association at the current time step).
        """
        if self.track_state == TrackState.Tentative:
            # if self.calls > self.n_init:
            print(f'track id in init state = {self.track_id} is deleted')
            self.track_state = TrackState.Deleted
        if self.last_seen > self.max_age:
            print(f'track id in max age = {self.track_id} is deleted')
            self.track_state = TrackState.Deleted
        self.last_seen += 1
        self.missed = True

    def is_tentative(self):
        """Returns True if this track is tentative (unconfirmed).
        """
        return self.track_state == TrackState.Tentative

    def is_confirmed(self):
        """Returns True if this track is confirmed."""
        return self.track_state == TrackState.Confirmed

    def is_deleted(self):
        """Returns True if this track is dead and should be deleted."""
        return self.track_state == TrackState.Deleted

    def is_missed(self):
        """Returns True if this track is dead and should be deleted."""
        return self.missed
