from pixel import Pixel
from flask import Blueprint, request, Response
from flipdot.connector import pixel, default_id, validate_id
from flipdot.models import Result
from flipdot.text_helpers import available_fonts, get_display_data, render_display_data, get_dimensions
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import threading
import time

DDB_LOCK = threading.Lock()

bp = Blueprint('display', __name__, url_prefix='/display')

def display_data_block_with_retry(displayNo: int, data: str) -> Result:
    acquired = DDB_LOCK.acquire(timeout=3)
    if not acquired:
        r  = Result()
        r.isOk = False
        r.isTimeout = True
        return r
    try:
        retryCount = 3
        err: str | None = None
        while retryCount > 0:
            try:
                pixel.display_data_block(displayNo, data)
                return Result()
            except ValueError as e:
                err = e.args
                retryCount -= 1
        res = Result()
        if err is not None:
            res.isOk = False
            res.msg = err
        return Result()
    finally:
        DDB_LOCK.release()

@bp.route('/image', methods = ['POST'])
def upload_file():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    imageFile = request.files['file']
    page = int(request.args.get('page'))
    img = Image.open(imageFile.stream)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = display_data_block_with_retry(id, data)
    return resp.toResponse()

@bp.route('/text', methods=["POST"])
def text():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    value = request.args.get('value')
    page = int(request.args.get('page'))
    font = request.args.get('font')
    if font is None:
        font = 'superstar'
    fontDef = available_fonts.get(font)
    if fontDef is None:
        Response("Font not found", status=404)
    img = Image.new("1", get_dimensions(id), (0))
    fontDef.drawText(img, 0, 0 + fontDef.topOffset, value, (255))
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = display_data_block_with_retry(id, data)
    return resp.toResponse()

@bp.route("/complex", methods=["POST"])
def complex():
    id = validate_id(request.args.get("id", default=default_id, type=int))
    page = int(request.args.get('page'))
    json_data = request.get_data()
    data = get_display_data(json_data)
    try:
        img = render_display_data(id, data)
    except ValueError as e:
        return Response(str(e.args), status=400)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = display_data_block_with_retry(id, data)
    return resp.toResponse()