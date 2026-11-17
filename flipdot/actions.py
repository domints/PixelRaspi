from flask import Blueprint, request, Response
from flipdot import connector
from flipdot.connector import validate_id

bp = Blueprint('actions', __name__, url_prefix='/actions')

def _display_id() -> int:
    return validate_id(request.args.get("id", default=connector.default_id, type=int))

@bp.route("/validators_block", methods = ['POST'])
def validators_block():
    value = request.args.get("blocked", default=False, type=bool)
    connector.pixel.set_validators_block(value)
    return Response(status=200)

@bp.route('/clear_pages', methods=['POST'])
def clear_pages():
    connector.pixel.delete_all_pages(_display_id())
    return Response(status=200)

@bp.route('/raw/ddb', methods=['POST'])
def display_raw_ddb():
    value = request.args.get('value')
    connector.pixel.display_data_block(_display_id(), value)
    return Response(status=200)
    