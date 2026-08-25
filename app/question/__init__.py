from flask import Blueprint

question_bp = Blueprint('question', __name__, url_prefix='/question')

from . import question
