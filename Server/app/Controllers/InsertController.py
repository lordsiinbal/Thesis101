
from flask import  request, jsonify, Blueprint
from mongoengine import *

post = Blueprint('post',__name__)

from app.Models.UserModel import dc_user
from app.Models.RoadModel import dc_road
from app.Models.ViolationModel import dc_violation
from app.Models.PlaybackModel import dc_playback


@post.route('/UserInsert', methods=['POST'])
def UserInsert():
    data = request.get_json()
    userInsert= dc_user()
    userInsert.username = data['username']
    userInsert.password = data['password']
    print(userInsert.username, userInsert.password)
    userInsert.save()
    print(userInsert.username, userInsert.password)
    return jsonify({"username": userInsert.username, "password": userInsert.password})

@post.route('/RoadInsert', methods=['POST'])
def RoadInsert():
    data = request.get_json()
    roadInsert = dc_road()
    roadInsert.roadID = data['roadID']
    roadInsert.roadName = data['roadName']
    roadInsert.roadCaptured = data['roadCaptured']
    roadInsert.roadBoundaryCoordinates = data['roadBoundaryCoordinates']
    roadInsert.save()
    return jsonify({"roadID":  roadInsert.roadID, "roadName": roadInsert.roadName,"roadCaptured": roadInsert.roadCaptured, "roadBoundaryCoordinates": roadInsert.roadBoundaryCoordinates})

@post.route('/ViolationInsert', methods=['POST'])
def ViolationInsert():
    data = request.get_json()
    violationInsert = dc_violation()
    violationInsert.violationID = data['violationID']
    violationInsert.vehicleID = data['vehicleID']
    violationInsert.roadName = data['roadName']
    violationInsert.lengthOfViolation = data['lengthOfViolation']   
    violationInsert.startDateAndTime = data['startDateAndTime']
    violationInsert.endDateAndTime = data['endDateAndTime']    
    violationInsert.save()
    return jsonify ({"violationID": violationInsert.violationID, "vehicleID": violationInsert.vehicleID,"roadName":violationInsert.roadName,"lengthOfViolation": violationInsert.lengthOfViolation, "startDateAndTime": violationInsert.startDateAndTime, "endDateAndTime": violationInsert.endDateAndTime})

@post.route('/PlaybackInsert', methods=['POST'])
def PlaybackInsert():
    data = request.get_json()
    playbackInsert = dc_playback()
    playbackInsert.playbackID = data['playbackID']
    playbackInsert.playbackVideo = data['playbackVideo']
    playbackInsert.duration = data['duration']
    playbackInsert.dateAndTime = data['dateAndTime']
    playbackInsert.roadName = data['roadName']
    playbackInsert.save()
    return jsonify ({"playbackID": playbackInsert.playbackID,"playbackVideo": playbackInsert.playbackVideo,"duration": playbackInsert.duration,"dateAndTime": playbackInsert.dateAndTime,"roadName": playbackInsert.roadName})

