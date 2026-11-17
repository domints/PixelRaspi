from flask import Blueprint, request
from flipdot import connector
from flipdot.connector import validate_id

bp = Blueprint('info', __name__, url_prefix='/info')

def _display_id() -> int:
    return validate_id(request.args.get("id", default=connector.default_id, type=int))

@bp.route("/factory_dentification")
def factory_id():
    return connector.pixel.get_factory_identification(_display_id())

@bp.route("/gid")
def gid():
    return connector.pixel.get_gid(_display_id())

@bp.route("/did")
def did():
    return connector.pixel.get_did(_display_id())

@bp.route("/available_commands")
def available_commands():
    return connector.pixel.get_available_commands(_display_id())