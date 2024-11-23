from enum import Enum
from typing import Dict, Optional
from flask import Response
from pydantic import BaseModel, ConfigDict, TypeAdapter

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
    
class DisplayData(BaseModel):
    model_config = ConfigDict()

    addition: Optional[Addition] = None
    lines: Optional[list[TextLine]] = None

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