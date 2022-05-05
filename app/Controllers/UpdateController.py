from flask import  request, jsonify, Blueprint
from mongoengine import *

put = Blueprint('put',__name__)

from app.Models.UserModel import dc_user
from app.Models.RoadModel import dc_road
from app.Models.ViolationModel import dc_violation
from app.Models.PlaybackModel import dc_playback



@put.route('/RoadUpdate', methods=['PUT'])
def RoadUpdate():
    data = request.get_json()
    print(data)
    # roadUpdate= dc_road()
    dc_road.objects(roadID=data['roadID']).update_one(roadName= data['roadName'])
    return jsonify(dc_road.objects(roadID=data['roadID']))

@put.route('/PlaybackUpdate', methods=['PUT'])
def PlaybackUpdate():
    data = request.get_json()
    # playbackUpdate = dc_playback()
    dc_playback.objects(playbackID=data['playbackID']).update_one(duration= data['duration'])
    return jsonify(dc_playback.objects(playbackID=data['playbackID'] ))

