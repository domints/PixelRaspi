from flask_openapi3 import APIBlueprint, Tag
from flipdot import connector
from flipdot.connector import resolve_id
from flipdot.models import DisplayIdQuery

bp = APIBlueprint('info', __name__, url_prefix='/info', abp_tags=[Tag(name='info')])

@bp.get("/factory_dentification", summary="Gets factory identification from display (firmware version etc)", responses={
    200: {"description": "Factory info."},
})
def factory_id(query: DisplayIdQuery):
    return connector.pixel.get_factory_identification(resolve_id(query.id))

@bp.get("/gid", summary="Gets information about display properties (size etc.)", responses={
    200: {"description": "GID."},
})
def gid(query: DisplayIdQuery):
    return connector.pixel.get_gid(resolve_id(query.id))

@bp.get("/did", summary="Gets device identification", responses={
    200: {"description": "DID."},
})
def did(query: DisplayIdQuery):
    return connector.pixel.get_did(resolve_id(query.id))

@bp.get("/available_commands", summary="Gets available commands", responses={
    200: {"description": "available commands."},
})
def available_commands(query: DisplayIdQuery):
    return connector.pixel.get_available_commands(resolve_id(query.id))