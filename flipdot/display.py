from flask import Blueprint, request, Response
from . import connector
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from flipdot.text_helpers import available_fonts

bp = Blueprint('display', __name__, url_prefix='/display')

@bp.route('/image', methods = ['POST'])
def upload_file():
    """
    Display image file
    ---
    description: Test
    parameters:
    - name: page
      in: query
      description: Page number, from 0 to probably 255
      required: true
      schema:
        type: int
    - name: file
      in: formData
      type: file
      description: The file to upload.
    responses:
        200:
            description: Image should be displayed.
    tags:
    - display
    """
    imageFile = request.files['file']
    page = int(request.args.get('page'))
    img = Image.open(imageFile.stream)
    imgArr = np.asarray(img)
    data = connector.px.create_data_block(connector.px.get_image_data(imgArr, page=page))
    resp = connector.px.display_data_block(0, data)
    if resp is None:
        return Response(resp, status=500)
    return Response(status=200)

@bp.route('/text', methods=["POST"])
def text():
    """
    Display single line of text
    ---
    parameters:
    - name: value
      in: query
      description: Text to be displayed
      required: true
      schema:
        type: string
    - name: page
      in: query
      description: Page to display on
      required: true
      schema:
        type: int
    - name: font
      in: query
      description: Font to render with. If not set using superstar.
      required: false
      schema:
        type: string
    responses:
        200:
            description: Text should be displayed.
    tags:
    - display
    """    
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
    data = connector.px.create_data_block(connector.px.get_image_data(imgArr, page=page))
    resp = connector.px.display_data_block(0, data)
    if resp is not None:
        return Response(resp, status=500)
    return Response(status=200)