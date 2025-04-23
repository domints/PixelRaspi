from flask import Blueprint, request, Response
from flipdot.connector import default_id, pixel, validate_id

bp = Blueprint('actions', __name__, url_prefix='/actions')

@bp.route("/validators_block", methods = ['POST'])
def validators_block():
    value = request.args.get("blocked", default=False, type=bool)
    pixel.set_validators_block(value)
    return Response(status=200)

@bp.route('/clear_pages', methods=['POST'])
def clear_pages():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    pixel.delete_all_pages(id)
    return Response(status=200)

@bp.route('/raw/ddb', methods=['POST'])
def display_raw_ddb():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    value = request.args.get('value')
    pixel.display_data_block(id, value)
    return Response(status=200)
    