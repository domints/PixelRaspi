from flask import Response
from flask_openapi3 import APIBlueprint, Tag
from flipdot import connector
from flipdot.connector import resolve_id
from flipdot.models import DisplayIdQuery, RawDdbQuery, ValidatorsBlockQuery

bp = APIBlueprint('actions', __name__, url_prefix='/actions', abp_tags=[Tag(name='actions')])

@bp.post("/validators_block", summary="Sets validators block, either block or unblock. Might display information on internal display.", responses={
    200: {"description": "Validators set correctly."},
})
def validators_block(query: ValidatorsBlockQuery):
    connector.pixel.set_validators_block(query.blocked)
    return Response(status=200)

@bp.post('/clear_pages', summary="Clear all pages (make display blank)", responses={
    200: {"description": "Pages cleared"},
})
def clear_pages(query: DisplayIdQuery):
    connector.pixel.delete_all_pages(resolve_id(query.id))
    return Response(status=200)

@bp.post('/raw/ddb', summary="Sends datablock to display. Should show it.", responses={
    200: {"description": "Datablock sent."},
})
def display_raw_ddb(query: RawDdbQuery):
    connector.pixel.display_data_block(resolve_id(query.id), query.value)
    return Response(status=200)
    