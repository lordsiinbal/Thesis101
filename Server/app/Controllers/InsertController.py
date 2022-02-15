
import os
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
    # roadInsert.roadBoundaryCoordinates = data['roadBoundaryCoordinates']
    filename = data['roadID']+".txt"
    # roi = open('%s.txt' %filename, "w")
    # roi.write(data['roadBoundaryCoordinates'])
   
    # roi.close()
    with open(filename, 'w') as roi:
        roi.write(data['roadBoundaryCoordinates'])
    print("filesave  ", filename)

    # with open('%s.txt' % data['roadID'], 'rb') as fd:
    #     dc_road.roadBoundaryCoordinates.put(fd, content_type = 'text/plain')
    # f = GridFSProxy()
    to_read = open('%s.txt' % data['roadID'], 'rb')
    roadInsert.roadBoundaryCoordinates.put(to_read, content_type = 'text/plain', filename=os.path.basename(to_read.name))
    to_read.close()
    # roadInsert.roadBoundaryCoordinates = f
    
    file=open(filename, "r")
    print(file.read())
    print(roadInsert.roadID)
    print(roadInsert.roadBoundaryCoordinates)
    print(roadInsert.roadBoundaryCoordinates.filename)
    print(roadInsert.roadBoundaryCoordinates.content_type)
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

