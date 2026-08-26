from flask import Blueprint

group_bp = Blueprint('group', __name__, url_prefix='/group')

from . import group, member
