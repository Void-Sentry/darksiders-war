from application.services import profile_service
from ..guards import cookie_required
from flask import jsonify, request
from .content import bp

@bp.route('/', methods=['GET'])
@cookie_required
def info():
    user_id = request.user['sub']
    res = profile_service.info(user_id)
    return jsonify({ "message": "profile info", "data": res }), 201

@bp.route('/followers', methods=['GET'])
@cookie_required
def followers():
    user_id = request.user['sub']
    res = profile_service.followers(user_id)
    return jsonify({ "message": "Followers count", "data": res }), 201
