from flask import Blueprint, request, Response
from . import display

bp = Blueprint('actions', __name__, url_prefix='/actions')

@bp.route("/validators_block", methods = ['POST'])
def validators_block():
    """
    Sets validators block, either block or unblock. Might display information on internal display.
    ---
    parameters:
    - name: blocked
      in: query
      description: Indicates whether validators should be blocked or not
      required: true
      schema:
        type: boolean

    responses:
          200:
            description: Validators set correctly.
    tags:
    - actions
    """
    value = request.args.get("blocked", default=False, type=bool)
    display.px.set_validators_block(value)
    return Response(status=200)
    