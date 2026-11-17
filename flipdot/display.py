from flask import Blueprint, request, Response
from flipdot import connector
from flipdot.connector import UnknownDisplayError, validate_id
from flipdot.models import Result
from flipdot.text_helpers import available_fonts, get_display_data, render_display_data, get_dimensions
from PIL import Image
from pixel.renderer.errors import PixelRenderError
import threading

DDB_LOCK = threading.Lock()

bp = Blueprint('display', __name__, url_prefix='/display')

def display_data_block_with_retry(displayNo: int, data) -> Result:
    acquired = DDB_LOCK.acquire(timeout=3)
    if not acquired:
        r = Result()
        r.isOk = False
        r.isTimeout = True
        return r
    try:
        retryCount = 3
        err: str | None = None
        while retryCount > 0:
            try:
                connector.pixel.display_data_block(displayNo, data)
                return Result()
            except ValueError as e:
                err = str(e)
                retryCount -= 1
        res = Result()
        res.isOk = False
        res.msg = err or "Display rejected the data block"
        return res
    finally:
        DDB_LOCK.release()

def show_image(display_no: int, image: Image.Image, page: int) -> Result:
    try:
        renderer = connector.get_renderer(display_no)
        kwargs = {"page": page, "threshold": 1}
        if connector.encoding:
            kwargs["encoding"] = connector.encoding
        block = renderer.render_image(image, **kwargs)
    except UnknownDisplayError:
        raise
    except (PixelRenderError, ValueError, KeyError) as e:
        res = Result()
        res.isOk = False
        res.msg = str(e)
        return res
    return display_data_block_with_retry(display_no, block)

@bp.route('/image', methods = ['POST'])
def upload_file():
    id = validate_id(request.args.get("id", default=connector.default_id, type=int))
    imageFile = request.files['file']
    page = int(request.args.get('page'))
    img = Image.open(imageFile.stream)
    resp = show_image(id, img, page)
    return resp.toResponse()

@bp.route('/text', methods=["POST"])
def text():
    id = validate_id(request.args.get("id", default=connector.default_id, type=int))
    value = request.args.get('value')
    page = int(request.args.get('page'))
    font = request.args.get('font')
    if font is None:
        font = 'superstar'
    fontDef = available_fonts.get(font)
    if fontDef is None:
        return Response("Font not found", status=404)
    img = Image.new("1", get_dimensions(id), (0))
    fontDef.drawText(img, 0, 0 + fontDef.topOffset, value, (255))
    resp = show_image(id, img, page)
    return resp.toResponse()

@bp.route("/complex", methods=["POST"])
def complex():
    id = validate_id(request.args.get("id", default=connector.default_id, type=int))
    page = int(request.args.get('page'))
    json_data = request.get_data()
    data = get_display_data(json_data)
    try:
        img = render_display_data(id, data)
    except ValueError as e:
        return Response(str(e.args), status=400)
    resp = show_image(id, img, page)
    return resp.toResponse()
