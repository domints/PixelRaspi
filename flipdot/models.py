from pydantic import BaseModel, ConfigDict


class TextLine(BaseModel):
    model_config = ConfigDict(strict=True)

    text: str
    font: str

class DisplayData(BaseModel):
    model_config = ConfigDict(strict=True)

    main_line: TextLine


def get_display_data(json_data: str) -> DisplayData:
    return DisplayData.model_validate_json(json_data)