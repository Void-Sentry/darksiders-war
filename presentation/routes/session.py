from ..guards import token_required, cookie_required
from flask import jsonify, request, make_response
from application.services import session_service
from .content import bp

@bp.route('/session', methods=['GET'])
@cookie_required
def active():
    return jsonify({ 'message': 'Session still active' }), 201

@bp.route('/session', methods=['POST'])
@token_required
def session():
    token = request.headers.get("Authorization").split(' ')[1]
    decoded = request.user
    sessionId, ttl = session_service.swap(decoded, token)

    response = make_response(jsonify({ 'message': 'Session created' }))

    response.set_cookie(
        key='sessionId',
        value=sessionId,
        httponly=True,
        secure=False,
        samesite='Strict',
        max_age=ttl,
        path='/'
    )

    return response, 201

@bp.route('/session', methods=['DELETE'])
@cookie_required
def invalidate():
    session_id = request.session_id
    session_service.invalidate(session_id)

    response = make_response(jsonify({ 'message': 'Session invalidated' }))

    response.set_cookie(
        key='sessionId',
        value=session_id,
        httponly=True,
        secure=False,
        samesite='Strict',
        max_age=0,
        path='/'
    )

    return response, 201
