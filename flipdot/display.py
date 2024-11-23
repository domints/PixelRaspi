from flask import Blueprint, request, Response
from flipdot.connector import pixel
from flipdot.text_helpers import available_fonts, get_display_data, render_display_data, get_dimensions
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pixel import Pixel

bp = Blueprint('display', __name__, url_prefix='/display')

def display_data_block(px: Pixel, page: int, data: str) -> str | None:
    retryCount = 3
    err: str | None = None
    while retryCount > 0:
        try:
            px.display_data_block(page, data)
            err = None
            retryCount = 0
        except ValueError as e:
            err = e.args
            retryCount -= 1
    return err

@bp.route('/image', methods = ['POST'])
def upload_file():
    imageFile = request.files['file']
    page = int(request.args.get('page'))
    img = Image.open(imageFile.stream)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = display_data_block(pixel, 0, data)
    if resp is not None:
        return Response(resp, status=500)
    return Response(status=200)

@bp.route('/text', methods=["POST"])
def text():
    value = request.args.get('value')
    page = int(request.args.get('page'))
    font = request.args.get('font')
    if font is None:
        font = 'superstar'
    fontDef = available_fonts.get(font)
    if fontDef is None:
        Response("Font not found", status=404)
    img = Image.new("1", get_dimensions(), (0))
    fontDef.drawText(img, 0, 0 + fontDef.topOffset, value, (255))
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = display_data_block(pixel, 0, data)
    if resp is not None:
        return Response(resp, status=500)
    return Response(status=200)

@bp.route("/complex", methods=["POST"])
def complex():
    page = int(request.args.get('page'))
    json_data = request.get_data()
    data = get_display_data(json_data)
    try:
        img = render_display_data(data)
    except ValueError as e:
        return Response(str(e.args), status=400)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    err = display_data_block(pixel, 0, data)
    if err is not None:
        return Response(err, status=500)
    return Response(status=200)
    pass