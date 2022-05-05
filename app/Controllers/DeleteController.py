from flask import request,jsonify, Blueprint
from mongoengine import *


delete = Blueprint('delete',__name__)



from app.Models.UserModel import dc_user
from app.Models.RoadModel import dc_road
from app.Models.ViolationModel import dc_violation
from app.Models.PlaybackModel import dc_playback

@delete.route('/ViolationDelete', methods=['DELETE'])
def ViolationDelete():
    data = request.get_json()
    dc_violation.objects(violationID = data['violationID']).delete()
    return jsonify(dc_violation.objects)

@delete.route('/RoadDelete', methods=['DELETE'])
def RoadDelete():   
    data = request.get_json()
    dc_road.objects(roadID = data['roadID']).delete()
    return jsonify(dc_road.objects)