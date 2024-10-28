
from flipdot.models import PxFont, get_fonts
from flipdot.text_helpers import BinaryFont, available_fonts


fonts: list[PxFont] = []
def initialize():
    global fonts
    with open('fonts/fonts.json', 'rb') as json_file:
        contents = json_file.read()
        fonts = get_fonts(contents)
    for f in fonts:
        if f.codepage != 'icon':
            available_fonts[f.name] = BinaryFont(f, f.height <= 8, f.codepage == 'cp1250' or f.codepage == 'cp1257')

    


