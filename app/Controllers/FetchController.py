from encodings import utf_8
from flask import jsonify, Blueprint, request
from mongoengine import *
from mongoengine import DoesNotExist

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

@get.route('/UserFetch', methods=['GET'])
def UserFetch():
    credentials = request.get_json()
    data = {"result":False}
    try:
        _ = dc_user.objects.get(username=credentials['username'],password=credentials['password'])
    except DoesNotExist as er:
        print("Response: ", er)
        return jsonify(data)
    data['result'] = True
    return jsonify(data)

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

@get.route('/RoadFetch', methods=['GET'])
def RoadFetch():
    # roadPic=dc_road.objects()
    # photo = roadPic.roadCaptured.read()
    # # content_type =roadPic.roadCaptured.content_type
    # print(photo)
    # # print(jsonify(dc_road.objects))
    

    data = []
    ids = request.get_json()
    #get only missing roads in client/images
    for id in ids:
        roadData = dc_road.objects.get(roadID=id)
        data.append({
            'roadID' : roadData.roadID,
            'roadName' : roadData.roadName,
            'roadBoundaryCoordinates' :roadData.roadBoundaryCoordinates,
            'roadCaptured' : str(roadData.roadCaptured.read().decode())
        }) 
    return jsonify(data)


# to lesssen time in loading in fethc road, get only road ids to check first if it exists in local device
@get.route('/RoadFetchIds', methods=['GET'])
def RoadFetchIds():

    data = []

    for roadPicture in dc_road.objects:
        data.append({
            'roadID' : roadPicture.roadID,
            'roadName' : roadPicture.roadName,
            'roadBoundaryCoordinates' :roadPicture.roadBoundaryCoordinates
        })
# numpy.asarray().tolist()
    return jsonify(data)


@get.route('/ViolationFetchAll', methods=['GET'])
def ViolationFetchAll():
    return jsonify(dc_violation.objects)

@get.route('/PlaybackFetchAll', methods=['GET'])
def PlaybackFetchAll():
    return jsonify(dc_playback.objects)

