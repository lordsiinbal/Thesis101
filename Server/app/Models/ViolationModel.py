from mongoengine import *



class dc_violation(Document):
    violationID = StringField()
    vehicleID  = StringField()
    roadName  = StringField()
    roadID = StringField()
    # violationRecord = FileField()
    lengthOfViolation  = StringField()
    startDateAndTime = DateField()
    endDateAndTime = DateField()

    def to_json(self):
        return{
            "violationID": self.violationID,
            "vehicleID": self.vehicleID,
            "roadName": self.roadName,
            "roadID": self.roadID,
            # "violationRecord": self.violationRecord,
            "lengthOfViolation": self.lengthOfViolation,
            "StartdateAndTime": self.startDateAndTime,
            "EnddateAndTime": self.endDateAndTime
        }