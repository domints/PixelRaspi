from flask import Blueprint, request
from flipdot.connector import pixel, default_id, validate_id

bp = Blueprint('info', __name__, url_prefix='/info')

@bp.route("/factory_dentification")
def factory_id():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    return pixel.get_factory_identification(id)

@bp.route("/gid")
def gid():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    return pixel.get_gid(id)

@bp.route("/did")
def did():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    return pixel.get_did(id)

@bp.route("/available_commands")
def available_commands():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    return pixel.get_available_commands(id)