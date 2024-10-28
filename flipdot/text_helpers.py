import abc
import codecs
from typing import Any, Dict, Optional
from flask import Blueprint, request, Response
from flipdot.connector import get_dimensions
from flipdot.models import CharD, DisplayData, AdditionType, PxFont, TextAlign, get_display_data
import io
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

default_big_font = "MiniMasa"
default_small_font = "uni05_53"

class BaseFont:
    def __init__(self, isTrueTrype: bool, name: str, height: int, topOffset: int, secondRowOffset: int, halfHeight: bool, hasDiacritics: bool):
        self.isTrueType = isTrueTrype
        self.name = name
        self.height = height
        self.topOffset = topOffset
        self.secondRowOffset = topOffset if secondRowOffset is None else secondRowOffset
        self.halfHeight = halfHeight
        self.hasDiacritics = hasDiacritics

    @abc.abstractmethod
    def drawText(self, img: Image, x: int, y: int, text: str, fill: Any | None = None, charSpace: int | None = None):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def calcWidth(self, text: str, charSpace: int | None = None) -> int:
        raise NotImplementedError()

class TTFFont(BaseFont):
    def __init__(self, name: str, format: str, nativeSize: int, topOffset: int = 0, halfHeight: bool = False, doubleOffset: int = 0, secondRowOffset: Optional[int] = None, hasDiacritics: bool = False):
        BaseFont.__init__(self, True, name, nativeSize, topOffset, secondRowOffset, halfHeight, hasDiacritics)
        self.format = format
        self.doubleOffset = doubleOffset
        
        self.imgFont = ImageFont.truetype(self.getPath(), self.height)

    def getPath(self) -> str:
        return f'fonts/{self.name}.{self.format}'
    
    def drawText(self, img: Image, x: int, y: int, text: str, fill: Any | None = None, charSpace: int | None = None):
        draw = ImageDraw.ImageDraw(img)
        draw.text((x, y), text, fill, font=self.imgFont)

    def calcWidth(self, text: str, charSpace: int | None = None) -> int:
        return int(math.ceil(self.imgFont.getlength(text))) - 1

    
class BinaryFont(BaseFont):
    def __init__(self, font: PxFont, halfHeight: bool, hasDiacritics: bool):
        BaseFont.__init__(self, True, font.name, font.height, 0, 0, halfHeight, hasDiacritics)
        self.pxFont = font
        pass

    def drawText(self, img: Image.Image, x: int, y: int, text: str, fill: Any | None = None, charSpace: int | None = None):
        chars = codecs.encode(text, self.pxFont.codepage, errors='replace')
        charSp = 1 if charSpace is None else charSpace
        currX = x
        for chr_code in chars:
            ch = None
            if chr_code in chars:
                ch = self.pxFont.chars[chr_code]
            if ch is not None:
                self.draw_char(img, ch, currX, y, fill)
                currX += ch.width + charSp

    def calcWidth(self, text: str, charSpace: int | None = None) -> int:
        chars = codecs.encode(text, self.pxFont.codepage, errors='replace')
        charSp = 1 if charSpace is None else charSpace
        currX = 0
        for str_ix in range(len(chars)):
            ch = None
            chr_code = chars[str_ix]
            if chr_code in chars:
                ch = self.pxFont.chars[chr_code]
            if ch is not None:
                currX += ch.width
            if str_ix < len(chars) - 1:
                currX += charSp
        return currX

    def draw_char(self, img: Image.Image, char: CharD, px: int | None = None, py: int | None = None, fill: Any | None = None):
        y = 0
        for r in char.rows:
            x = 0
            for p in r:
                if p == '#':
                    px_x = px + x
                    px_y = py + y
                    if px_x < img.width and px_y < img.height:
                        img.putpixel((px_x, px_y), fill if fill is not None else 1)
                x += 1
                pass
            y += 1
        pass

available_fonts: Dict[str, BaseFont] = {
    'joystix': TTFFont("joystix", "otf", 10, 2, hasDiacritics=True),
    'superstar': TTFFont("superstar", "ttf", 16, hasDiacritics=True),
    'super_mario_bros': TTFFont("super_mario_bros", "ttf", 8, halfHeight=True, doubleOffset=-1, hasDiacritics=True),
    'KiwiSoda': TTFFont("KiwiSoda", "ttf", 16, hasDiacritics=True),
    'PressStart2P': TTFFont("PressStart2P", "ttf", 8, halfHeight=True, doubleOffset=1, hasDiacritics=True),
    'gosub': TTFFont("gosub", "otf", 7, -1, halfHeight=True, hasDiacritics=True),
    'tandysoft': TTFFont("tandysoft", "otf", 10, 1, hasDiacritics=True),
    '2a03': TTFFont("2a03", "ttf", 16, 1, hasDiacritics=True),
    'Pixolletta': TTFFont("Pixolletta", "ttf", 10, 4, hasDiacritics=True),
    'MiniMasa': TTFFont("MiniMasa", "ttf", 12, -2, hasDiacritics=True),
    'MiniSet2': TTFFont("MiniSet2", "ttf", 8, 3, halfHeight=False, hasDiacritics=True),
    'uni05_53': TTFFont("uni05_53", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_54': TTFFont("uni05_54", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_63': TTFFont("uni05_63", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'uni05_64': TTFFont("uni05_64", "ttf", 8, halfHeight=True, hasDiacritics=True),
    'axion14': TTFFont("axion14", "ttf", 14, 1),
    'pixol': TTFFont("pixol", "ttf", 10, 4),
    'twin6': TTFFont("twin6", "ttf", 6, 1, halfHeight=True, doubleOffset=2),
    'twin14': TTFFont("twin14", "ttf", 10, 1),
    'cg': TTFFont("cg", "ttf", 5, 2, halfHeight=2, secondRowOffset=1)
}

def calc_width(font: ImageFont.ImageFont, text: str):
    return int(math.ceil(font.getlength(text))) - 1

def draw_text(img: Image.Image,
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
    text_width = fontDef.calcWidth(text)
    reduced = False
    original_y = y
    colourVal = 255
    if invert:
        colourVal = 0
        height = (8 if fontDef.halfHeight else 16)
    
    drawer = ImageDraw.ImageDraw(img)

    if not isAddition and text_width > max_width and auto_line_break:
        fontDef = available_fonts[default_small_font]
        text_width = fontDef.calcWidth(text)
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
                width = fontDef.calcWidth(tempLine)
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
        l1_width = fontDef.calcWidth(firstLine)
        l2_width = fontDef.calcWidth(secondLine)
        l1_leftover = max(0, max_width - l1_width)
        l2_leftover = max(0, max_width - l2_width)
        l1x = x
        l2x = x
        if align == TextAlign.Center:
            l1x += math.floor(l1_leftover / 2)
            l2x += math.floor(l2_leftover / 2)
        elif align == TextAlign.Right:
            l1x += l1_leftover
            l2x += l2_leftover
        fontDef.drawText(img, l1x, y + fontDef.topOffset, firstLine, (colourVal))
        fontDef.drawText(img, l2x, y + fontDef.secondRowOffset + 8, secondLine, (colourVal))
    else:
        if invert:
            drawer.rectangle((x, y, x + (text_width - 1 if isAddition else max_width), min(16, y + height)), fill=(255), width=0)
        leftover = max(0, max_width - text_width)
        lx = x
        if align == TextAlign.Center:
            lx += math.floor(leftover / 2)
        elif align == TextAlign.Right:
            lx += leftover
        fontDef.drawText(img, lx, y + (fontDef.topOffset if not isSecondRow else fontDef.secondRowOffset), text, (colourVal))
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
    left_text_margin = 0
    if data.addition is not None:
        if data.addition.addition_type == AdditionType.Text:
            add_font = default_big_font
            if data.addition.font is not None:
                add_font = data.addition.font
            left_text_margin = draw_text(img, add_font, data.addition.text, 0, 0, img.width, data.addition.invert, isAddition=True) + 1
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
            draw_text(img, font, data.lines[i].text, left_text_margin, i * 8, img.width - left_text_margin, data.lines[i].invert, data.lines[i].auto_break if singleLine else False, True if i == 1 else False, False, data.lines[i].align)

    return img

bp = Blueprint('text', __name__, url_prefix='/text')

@bp.route("/fonts")
def get_fonts():
    result = []
    for f in available_fonts:
        fd = available_fonts[f]
        o = {'name': fd.name, 'halfHeight': fd.halfHeight, 'hasDiacritics': fd.hasDiacritics, 'isBinary': not fd.isTrueType }
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
