import datetime
from mongoengine import *



class dc_violation(Document):
    violationID = StringField()
    vehicleID  = StringField()
    roadName  = StringField()
    roadID = StringField()
    violationRecord = StringField()
    lengthOfViolation  = StringField()
    startDateAndTime = StringField()
    endDateAndTime = StringField()
    frameStart = StringField()
    vehicleClass = StringField()
    
    

    def to_json(self):
        return{
            "violationID": self.violationID,
            "vehicleID": self.vehicleID,
            "roadName": self.roadName,
            "roadID": self.roadID,
            "violationRecord": self.violationRecord,
            "lengthOfViolation": self.lengthOfViolation,
            "startDateAndTime": self.startDateAndTime,
            "endDateAndTime": self.endDateAndTime,
            "frameStart": self.frameStart,
            "vehicleClass": self.vehicleClass
            
            
        }