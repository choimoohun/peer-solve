from flask import Blueprint

question_api_bp = Blueprint('question_api', __name__, url_prefix='/question')
question_page_bp = Blueprint('question_page', __name__, url_prefix='/question')

from . import question_api
from . import question_page
