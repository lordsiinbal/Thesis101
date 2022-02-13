from flask import jsonify, Blueprint
from mongoengine import *


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
    return jsonify(dc_road.objects)

@get.route('/ViolationFetchAll', methods=['GET'])
def ViolationFetchAll():
    return jsonify(dc_violation.objects)

@get.route('/PlaybackFetchAll', methods=['GET'])
def PlaybackFetchAll():
    return jsonify(dc_playback.objects)

