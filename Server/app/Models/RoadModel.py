from mongoengine import *

class dc_road(Document):
    roadID = StringField()
    roadName  = StringField()
    roadCaptured  = ListField()
    roadBoundaryCoordinates  = FileField()

    def to_json(self):
        return{
            "roadID": self.roadID,
            "roadName": self.roadName,
            "roadCaptured": self.roadCaptured,
            "roadBoundaryCoordinates": self.roadBoundaryCoordinates
        }