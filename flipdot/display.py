from flask import Blueprint, request, Response
from . import connector
from PIL import Image
import numpy as np

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
      