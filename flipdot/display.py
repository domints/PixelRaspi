from flask import Response
from flask_openapi3 import APIBlueprint, FileStorage, Tag
from flipdot import connector
from flipdot.connector import UnknownDisplayError, resolve_id
from flipdot.models import DisplayData, PageQuery, Result, TextQuery
from flipdot.text_helpers import available_fonts, build_content_layers, render_display_data, get_dimensions
from PIL import Image
from pixel.renderer.errors import PixelRenderError
from pydantic import BaseModel, Field
import threading

DDB_LOCK = threading.Lock()

bp = APIBlueprint('display', __name__, url_prefix='/display', abp_tags=[Tag(name='display')])

class ImageForm(BaseModel):
    file: FileStorage = Field(description="The file to upload.")

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

def show_composite(display_no: int, layers, page: int) -> Result:
    renderer = connector.get_renderer(display_no)
    kwargs = {"page": page}
    if connector.encoding:
        kwargs["encoding"] = connector.encoding
    block = renderer.render_composite(layers, **kwargs)
    return display_data_block_with_retry(display_no, block)

@bp.post('/image', summary="Display image file", responses={200: {"description": "Image should be displayed."}})
def upload_file(query: PageQuery, form: ImageForm):
    img = Image.open(form.file.stream)
    resp = show_image(resolve_id(query.id), img, query.page)
    return resp.toResponse()

@bp.post('/text', summary="Display single line of text", responses={
    200: {"description": "Text should be displayed."},
    404: {"description": "Font not found, or no such display id."},
})
def text(query: TextQuery):
    font = query.font or 'superstar'
    fontDef = available_fonts.get(font)
    if fontDef is None:
        return Response("Font not found", status=404)
    display_id = resolve_id(query.id)
    img = Image.new("1", get_dimensions(display_id), (0))
    fontDef.drawText(img, 0, 0 + fontDef.topOffset, query.value, (255))
    resp = show_image(display_id, img, query.page)
    return resp.toResponse()

@bp.post("/complex", summary="Display layered content", responses={
    200: {"description": "Page should be displayed."},
    400: {"description": "Invalid request, or this panel cannot scroll or fit the layers."},
})
def complex(query: PageQuery, body: DisplayData):
    """Show the legacy addition/lines layout, or a list of placed layers.

    A layer is text, an icon name, or a base64 image. Set ``scroll`` on a layer to pan
    it in hardware. Scrolling requires an LPC panel and an image wider than that panel
    (or taller, when ``scroll_vertical`` is set).
    """
    display_id = resolve_id(query.id)
    try:
        if body.layers:
            resp = show_composite(display_id, build_content_layers(body.layers), query.page)
        else:
            resp = show_image(display_id, render_display_data(display_id, body), query.page)
    except UnknownDisplayError:
        raise
    except (ValueError, PixelRenderError, KeyError) as e:
        return Response(str(e), status=400)
    return resp.toResponse()
