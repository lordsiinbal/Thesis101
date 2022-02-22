from encodings import utf_8
from flask import jsonify, Blueprint
from mongoengine import *
import numpy
import pandas as pd


get = Blueprint('get',__name__)


from app.Models.UserModel import dc_user
from app.Models.RoadModel import dc_road
from app.Models.ViolationModel import dc_violation
from app.Models.PlaybackModel import dc_playback



@get.route('/UserFetchAll', methods=['GET'])
def UserFetchAll():
    return jsonify(dc_user.objects)

@get.route('/RoadFetchAll', methods=['GET'])
def RoadFetchAll():
    # roadPic=dc_road.objects()
    # photo = roadPic.roadCaptured.read()
    # # content_type =roadPic.roadCaptured.content_type
    # print(photo)
    # # print(jsonify(dc_road.objects))
    

    data = []

    for roadPicture in dc_road.objects:
        # roi = open('asd.txt', "w")
        # # roi.write(str(roadPicture.roadCaptured.read().decode()))
        # roi.close()
        data.append({
            'roadID' : roadPicture.roadID,
            'roadName' : roadPicture.roadName,
            'roadBoundaryCoordinates' :roadPicture.roadBoundaryCoordinates,
            'roadCaptured' : str(roadPicture.roadCaptured.read().decode())
        })
# numpy.asarray().tolist()
    return jsonify(data)

@get.route('/ViolationFetchAll', methods=['GET'])
def ViolationFetchAll():
    return jsonify(dc_violation.objects)

@get.route('/PlaybackFetchAll', methods=['GET'])
def PlaybackFetchAll():
    return jsonify(dc_playback.objects)

