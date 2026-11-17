from enum import Enum
from typing import Dict, Optional
from flask import Response
from pydantic import BaseModel, ConfigDict, Field, RootModel, TypeAdapter

class AdditionType(Enum):
    Icon = 'icon'
    Text = 'text'

class TextAlign(Enum):
    Left = 'left'
    Center = 'center'
    Right = 'right'

class VerticalAlign(Enum):
    Top = 'top'
    Middle = 'middle'
    Bottom = 'bottom'

class Addition(BaseModel):
    model_config = ConfigDict()

    addition_type: AdditionType
    text: Optional[str] = None
    font: Optional[str] = None
    icon: Optional[str] = None
    invert: bool = False

class TextLine(BaseModel):
    model_config = ConfigDict()

    text: str
    font: Optional[str] = None
    invert: bool = False
    auto_break: bool = True
    align: TextAlign = TextAlign.Left

class Span(BaseModel):
    model_config = ConfigDict()

    text: str = ''
    valign: VerticalAlign = 'top'
    font: Optional[str] = None

class Block(BaseModel):
    model_config = ConfigDict()
    invert: bool = False
    top: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None
    right: Optional[int] = None
    spans: list[str | Span] = []
    
class ScrollDirection(Enum):
    Rtl = 'rtl'
    Ltr = 'ltr'

class ContentLayer(BaseModel):
    """One image on the page. Supply exactly one of text, icon, or image.

    ``bottom`` is the row above the bottom of the panel. Later layers paint over
    earlier ones. ``scroll`` is native hardware scrolling and only works on an LPC panel.
    """
    model_config = ConfigDict()

    text: Optional[str] = None
    font: Optional[str] = None
    icon: Optional[str] = Field(None, description="Icon name, without the .png suffix.")
    image: Optional[str] = Field(None, description="Base64-encoded image file.")
    left: int = Field(0, ge=0)
    bottom: int = Field(0, ge=0)
    invert: bool = False
    scroll: bool = False
    scroll_vertical: bool = False
    scroll_direction: ScrollDirection = ScrollDirection.Rtl
    scroll_rate: int = Field(40, ge=0, description="LPC scroll speed. 0 stays still. Motion saturates near 40.")
    window_width: Optional[int] = Field(None, ge=1, description="On-screen window. Defaults to the panel width, or height when scrolling vertically.")

class DisplayData(BaseModel):
    model_config = ConfigDict()

    addition: Optional[Addition] = None
    lines: Optional[list[TextLine]] = Field(None, max_length=2)
    layers: Optional[list[ContentLayer]] = Field(
        None,
        description="When set, these layers are the page. addition and lines are ignored.",
    )

class CharD(BaseModel):
    model_config = ConfigDict()

    height: int = 0
    width: int = 0
    code: int = 0
    rows: list[str] = []

class PxFont(BaseModel):
    model_config = ConfigDict()

    name: str = ''
    height: int = 0
    base: int = 0
    mid: int = 0
    top: int = 0
    codepage: str = ''
    chars: Dict[int, CharD] = {}

class Result():
    isOk: bool = True
    isTimeout: bool = False
    msg: str | None = None
    def toResponse(self):
        code = 200
        msg = None
        if self.isTimeout:
            code = 420
            msg = "Calm down, display can't handle you."
        elif not self.isOk:
            code = 500
            msg = self.msg
        return Response(msg, status=code)

def get_display_data(json_data: str) -> DisplayData:
    return DisplayData.model_validate_json(json_data)

def get_blocks(json_data: str) -> list[Block]:
    ta = TypeAdapter(list[Block])
    return ta.validate_json(json_data)

def get_fonts(json_data: bytes) -> list[PxFont]:
    ta = TypeAdapter(list[PxFont])
    return ta.validate_json(json_data)

class DisplayIdQuery(BaseModel):
    id: Optional[int] = Field(
        None,
        description="Decimal display address. Requests without id go to the first panel that answered.",
    )

class PageQuery(DisplayIdQuery):
    page: int = Field(description="Page number, from 0 to probably 255")

class TextQuery(PageQuery):
    value: str = Field(description="Text to be displayed")
    font: Optional[str] = Field(None, description="Font to render with. If not set, superstar is used.")

class ValidatorsBlockQuery(BaseModel):
    blocked: bool = Field(False, description="Indicates whether validators should be blocked or not")

class RawDdbQuery(DisplayIdQuery):
    value: str = Field(description="Datablock value to send")

class BlockList(RootModel[list[Block]]):
    pass

class FontInfo(BaseModel):
    name: str
    halfHeight: bool
    hasDiacritics: bool
    isBinary: bool

class FontList(RootModel[list[FontInfo]]):
    pass

class IconList(RootModel[list[str]]):
    pass