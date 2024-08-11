from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AdditionType(Enum):
    Icon = 'icon'
    Text = 'text'

class TextAlign(Enum):
    Left = 'left'
    Center = 'center'
    Right = 'right'

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

class DisplayData(BaseModel):
    model_config = ConfigDict()

    addition: Optional[Addition] = None
    lines: Optional[list[TextLine]] = None



def get_display_data(json_data: str) -> DisplayData:
    return DisplayData.model_validate_json(json_data)