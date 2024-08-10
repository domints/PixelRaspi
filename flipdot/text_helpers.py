from flask import Blueprint, request, Response
import json

class FontDef:
    def __init__(self, name: str, format: str, nativeSize: int, topOffset: int = 0, halfHeight: bool = False, doubleOffset: int = 0):
        self.name = name
        self.format = format
        self.nativeSize = nativeSize
        self.topOffset = topOffset
        self.halfHeight = halfHeight

    def getPath(self) -> str:
        return f'fonts/{self.name}.{self.format}'

available_fonts = {
    'joystix': FontDef("joystix", "otf", 10, 2),
    'superstar': FontDef("superstar", "ttf", 16),
    'super_mario_bros': FontDef("super_mario_bros", "ttf", 8, halfHeight=True, doubleOffset=-1),
    'KiwiSoda': FontDef("KiwiSoda", "ttf", 16),
    'PressStart2P': FontDef("PressStart2P", "ttf", 8, halfHeight=True, doubleOffset=1),
    'Orange_Kid': FontDef("Orange_Kid", "otf", 16),
    'Pixel_Gosub': FontDef("Pixel_Gosub", "otf", 7, -1, halfHeight=True),
    'Pixel_Tandysoft': FontDef("Pixel_Tandysoft", "otf", 10, 1),
    '2a03': FontDef("2a03", "ttf", 16, 1),
    'Pixolletta': FontDef("Pixolletta", "ttf", 10, 4),
    'MiniMasa': FontDef("MiniMasa", "ttf", 12, -4),
    'MiniSet2': FontDef("MiniSet2", "ttf", 8, 3, halfHeight=False),
    'uni05_53': FontDef("uni05_53", "ttf", 8, halfHeight=True),
    'uni05_54': FontDef("uni05_54", "ttf", 8, halfHeight=True),
    'uni05_63': FontDef("uni05_63", "ttf", 8, halfHeight=True),
    'uni05_64': FontDef("uni05_64", "ttf", 8, halfHeight=True),
}

bp = Blueprint('text', __name__, url_prefix='/text')

@bp.route("/fonts")
def get_fonts():
    """
    Gets available fonts
    ---
    responses:
        200:
            description: List of available fonts.
    """
    result = []
    for f in available_fonts:
        fd = available_fonts[f]
        o = {'name': fd.name, 'halfHeight': fd.halfHeight }
        result.append(o)

    return Response(json.dumps(result), status=200, content_type="text/json")