from mongoengine import *



class dc_playback(Document):
    playbackID = StringField()
    playbackVideo = StringField()
    duration = StringField()
    roadName = StringField()
    dateAndTime = DateTimeField()

    def to_json(self):
        return{
            "playbackID": self.playbackID,
            "playbackVideo": self.playbackVideo,
            "duration": self.duration,
            "dateAndTime": self.dateAndTime,
            "roadName": self.roadName
        }
