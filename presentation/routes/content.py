from flask import Blueprint

bp = Blueprint('content', __name__, url_prefix='/profile')

def initialize_routes(app):
    from . import profile, session
    app.register_blueprint(bp)