from flask import Blueprint
from . import display

bp = Blueprint('info', __name__, url_prefix='/info')

@bp.route("/factory_dentification")
def factory_id():
    """
    Gets factory identification from display (firmware version etc)
    ---
    responses:
          200:
            description: Factory info.
    tags:
    - info
    """
    return display.px.get_factory_identification(0)

@bp.route("/gid")
def gid():
    """
    Gets information about display properties (size etc.)
    ---
    responses:
          200:
            description: GID.
    tags:
    - info
    """
    return display.px.get_gid(0)

@bp.route("/did")
def did():
    """
    Gets device identification
    ---
    responses:
          200:
            description: DID.
    tags:
    - info
    """
    return display.px.get_did(0)

@bp.route("/available_commands")
def available_commands():
    """
    Gets available commands
    ---
    responses:
          200:
            description: available commands.
    tags:
    - info
    """
    return display.px.get_available_commands(0)