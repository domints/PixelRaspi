from flask import Blueprint
from flipdot.connector import pixel

bp = Blueprint('info', __name__, url_prefix='/info')

@bp.route("/factory_dentification")
def factory_id():
    return pixel.get_factory_identification(0)

@bp.route("/gid")
def gid():
    return pixel.get_gid(0)

@bp.route("/did")
def did():
    return pixel.get_did(0)

@bp.route("/available_commands")
def available_commands():
    return pixel.get_available_commands(0)