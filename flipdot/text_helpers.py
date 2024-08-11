from typing import Optional
from flask import Blueprint, request, Response
from flipdot.connector import get_dimensions
from flipdot.models import DisplayData, AdditionType, TextAlign, get_display_data
import io
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

default_big_font = "MiniMasa"
default_small_font = "uni05_53"

class FontDef:
    def __init__(self, name: str, format: str, nativeSize: int, topOffset: int = 0, halfHeight: bool = False, doubleOffset: int = 0, secondRowOffset: Optional[int] = None, hasDiacritics: bool = False):
        self.name = name
        self.format = format
        self.nativeSize = nativeSize
        self.topOffset = topOffset
        self.halfHeight = halfHeight
        self.hasDiacritics = hasDiacritics
        self.doubleOffset = doubleOffset
        self.secondRowOffset = topOffset if secondRowOffset is None else secondRowOffset

    def getPath(self) -> str:
        return f'fonts/{self.name}.{self.format}'

available_fonts = {
    'joystix': FontDef("joystix", "otf", 10, 2, hasDiacritics=True),
    'superstar': FontDef("superstar", "ttf", 16, hasDiacritics=True),
    'super_mario_bros': FontDef("super_mario_bros", "ttf", 8, halfHeight=True, doubleOffset=-1, hasDiacritics=True),
    'KiwiSoda': FontDef("KiwiSoda", "ttf", 16, hasDiacritics=True),
    'PressStart2P': FontDef("PressStart2P", "ttf", 8, halfHeight=True, doubleOffset=1, hasDiacritics=True),
    'gosub': FontDef("gosub", "otf", 7, -1, halfHeight=True, hasDiacritics=True),
    'tandysoft': FontDef("tandysoft", "otf", 10, 1, hasDiacritics=True),
    '2a03': FontDef("2a03", "ttf", 16, 1, hasDiacritics=True),
    'Pixolletta': FontDef("Pixolletta", "ttf", 10, 4, hasDiacritics=True),
    'MiniMasa': FontDef("MiniMasa", "ttf", 12, -2, hasDiacritics=True),
    'MiniSet2': FontDef("MiniSet2", "ttf", 8, 3, halfHeight=False, hasDiacritics=True),
    'uni05_53': FontDef("uni05_53", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_54': FontDef("uni05_54", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_63': FontDef("uni05_63", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_64': FontDef("uni05_64", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'axion14': FontDef("axion14", "ttf", 14, 1),
    'pixol': FontDef("pixol", "ttf", 10, 4),
    'twin6': FontDef("twin6", "ttf", 6, 1, halfHeight=True, doubleOffset=2),
    'twin14': FontDef("twin14", "ttf", 10, 1),
    'cg': FontDef("cg", "ttf", 5, 2, halfHeight=2, secondRowOffset=1)
}

def calc_width(font: ImageFont.ImageFont, text: str):
    return int(math.ceil(font.getlength(text))) - 1

def draw_text(drawer: ImageDraw.ImageDraw,
              font: str,
              text: str,
              x: int,
              y: int,
              max_width: int,
              invert: bool = False,
              auto_line_break: bool = False,
              isSecondRow: bool = False,
              isAddition: bool = False,
              align: TextAlign = TextAlign.Left) -> int:
    text = text.strip()
    fontDef = available_fonts[font]
    if fontDef is None:
        raise ValueError(f"No such font ({font}) available.")
    usr_font = ImageFont.truetype(fontDef.getPath(), fontDef.nativeSize)
    text_width = calc_width(usr_font, text)
    reduced = False
    original_y = y
    colourVal = 255
    if invert:
        colourVal = 0
        height = (8 if fontDef.halfHeight else 16)
    
    if not isAddition and text_width > max_width and auto_line_break:
        fontDef = available_fonts[default_small_font]
        usr_font = ImageFont.truetype(fontDef.getPath(), fontDef.nativeSize)
        text_width = calc_width(usr_font, text)
        y += 4
        reduced = True
    if text_width > max_width and reduced and ' ' in text:
        y = original_y
        words = text.split(' ')
        firstLine = ''
        secondLine = ''
        firstLineFull = False
        for i in range(0, len(words)):
            if not firstLineFull:
                tempLine = (firstLine + ' ' + words[i]) if i > 0 else words[i]
                width = calc_width(usr_font, tempLine)
                if width > max_width:
                    firstLineFull = True
                    secondLine = words[i]
                    if i == 0:
                        firstLine = words[0]
                else:
                    firstLine = tempLine
            else:
                secondLine += words[i] + ' '
        height = 16
        if invert:
            drawer.rectangle((x, y, x + max_width, min(16, y + height)), fill=(255), width=0)
        l1_width = calc_width(usr_font, firstLine)
        l2_width = calc_width(usr_font, secondLine)
        l1_leftover = max(0, max_width - l1_width)
        l2_leftover = max(0, max_width - l2_width)
        l1x = x
        l2x = x
        if align == TextAlign.Center:
            l1x += l1_leftover / 2
            l2x += l2_leftover / 2
        elif align == TextAlign.Right:
            l1x += l1_leftover
            l2x += l2_leftover
        drawer.text((l1x, y + fontDef.topOffset), firstLine, (colourVal), font=usr_font)
        drawer.text((l2x, y + fontDef.secondRowOffset + 8), secondLine, (colourVal), font=usr_font)
    else:
        if invert:
            drawer.rectangle((x, y, x + (text_width - 1 if isAddition else max_width), min(16, y + height)), fill=(255), width=0)
        leftover = max(0, max_width - text_width)
        lx = x
        if align == TextAlign.Center:
            lx += leftover / 2
        elif align == TextAlign.Right:
            lx += leftover
        drawer.text((lx, y + fontDef.topOffset if not isSecondRow else fontDef.secondRowOffset), text, (colourVal), font=usr_font)
    return text_width

def draw_icon(displayImage: Image.Image, name: str, x: int, y: int, invert: bool = False) -> int:
    iconPath = f"./icons/{name}.png"
    if not os.path.isfile(iconPath):
        raise ValueError(f"No icon '{name}' found.")
    icon = Image.open(iconPath)
    if not invert:
        icon = icon.convert("RGB")
        icon = ImageOps.invert(icon)
    displayImage.paste(icon, (x, y))
    return icon.width


def render_display_data(data: DisplayData) -> Image.Image:
    dimensions = get_dimensions()
    print(f'Render Display size, width {dimensions.width}x{dimensions.height}')
    img = Image.new("1", dimensions, (0))
    d_usr = ImageDraw.Draw(img)
    left_text_margin = 0
    if data.addition is not None:
        if data.addition.addition_type == AdditionType.Text:
            add_font = default_big_font
            if data.addition.font is not None:
                add_font = data.addition.font
            left_text_margin = draw_text(d_usr, add_font, data.addition.text, 0, 0, img.width, data.addition.invert, isAddition=True) + 1
        elif data.addition.addition_type == AdditionType.Icon:
            left_text_margin = draw_icon(img, data.addition.icon, 0, 0, data.addition.invert)
    if data.lines is not None and len(data.lines) > 0:
        if len(data.lines) > 2:
            raise ValueError("Cannot display more than 2 lines")
        singleLine = len(data.lines) == 1
        for i in range(0, len(data.lines)):
            font = default_big_font if singleLine else default_small_font
            if data.lines[i].font is not None:
                font = data.lines[i].font
            draw_text(d_usr, font, data.lines[i].text, left_text_margin, i * 8, img.width - left_text_margin, data.lines[i].invert, data.lines[i].auto_break if singleLine else False, True if i == 1 else False, False, data.lines[i].align)

    return img

bp = Blueprint('text', __name__, url_prefix='/text')

@bp.route("/fonts")
def get_fonts():
    result = []
    for f in available_fonts:
        fd = available_fonts[f]
        o = {'name': fd.name, 'halfHeight': fd.halfHeight, 'hasDiacritics': fd.hasDiacritics }
        result.append(o)

    return Response(json.dumps(result), status=200, content_type="text/json")

@bp.route("/icons")
def get_icons():
    iconFiles = os.listdir("./icons")
    result = []
    for icon in iconFiles:
        result.append(icon.split('.')[0])
    return Response(json.dumps(result), status=200, content_type="text/json")
    

@bp.route("/render_text", methods=["POST"])
def get_rendered_text():
    json_data = request.get_data()
    data = get_display_data(json_data)
    try:
        img = render_display_data(data)
    except ValueError as e:
        return Response(str(e.args), status=400)
    imgByteArr = io.BytesIO()
    img_resized = img.resize((img.width * 8, img.height * 8))
    img_resized.save(imgByteArr, format='PNG')
    return Response(imgByteArr.getvalue(), status=200, mimetype="image/png")
