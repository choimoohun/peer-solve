'''
  "group": {
    "_id": "ObjectId",
    "name": "String",
    "members": [
      "ObjectId (user_profile._id)"
    ],
    "questions": [
      "ObjectId (question._id)"
    ],
    "owner": "ObjectId (user_profile._id)",
    "at_create": "Timestamp",
    "at_update": "Timestamp"
  },
'''

from flask import jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from zoneinfo import ZoneInfo

from . import group_bp
from ..db import db