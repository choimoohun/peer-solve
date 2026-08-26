from flask import Blueprint
from .auth import auth_bp
from .group import group_bp
from .question import question_api_bp, question_page_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')
page_bp = Blueprint('page', __name__)

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(group_bp)
api_bp.register_blueprint(question_api_bp)

page_bp.register_blueprint(question_page_bp)