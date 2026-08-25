from flask import Blueprint

auth_bp = Blueprint('group', __name__, url_prefix='/group')

from . import group
