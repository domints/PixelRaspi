from flask import Blueprint, request, Response
from flipdot.connector import pixel, display_width, display_height
from flipdot.text_helpers import available_fonts, get_display_data, render_display_data
from PIL import Image, ImageDraw, ImageFont
import numpy as np

bp = Blueprint('display', __name__, url_prefix='/display')

@bp.route('/image', methods = ['POST'])
def upload_file():
    imageFile = request.files['file']
    page = int(request.args.get('page'))
    img = Image.open(imageFile.stream)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = pixel.display_data_block(0, data)
    if resp is None:
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
    img = Image.new("1", (84, 16), (0))
    d_usr = ImageDraw.Draw(img)
    usr_font = ImageFont.truetype(fontDef.getPath(), fontDef.nativeSize)
    d_usr.text((0, fontDef.topOffset), value,(255), font=usr_font)
    imgArr = np.asarray(img)
    data = pixel.create_data_block(pixel.get_image_data(imgArr, page=page))
    resp = pixel.display_data_block(0, data)
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
    resp = pixel.display_data_block(0, data)
    if resp is not None:
        return Response(resp, status=500)
    return Response(status=200)
    pass