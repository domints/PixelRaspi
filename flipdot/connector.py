from collections import namedtuple
from pixel import Pixel

from flipdot.pixelmock import PixelMock

pixel: Pixel = None
display_width: int = 0
display_height: int = 0

Dimensions = namedtuple('Dimensions', ['width', 'height'])

def start_pixel(port: str, pin: int | None = None, useMock: bool = False):
    global pixel
    global display_width
    global display_height
    if useMock:
        pixel = PixelMock()
    else:
        pixel = Pixel(port, pin)
        pixel.open()
    gid = pixel.get_gid(0)
    parts = gid.split('/')
    dimensions = parts[0].split('x')
    display_width = int(dimensions[0][1:])
    display_height = int(dimensions[1])
    print(f'Display width: {display_width}, height: {display_height}')

def get_dimensions() -> Dimensions:
    return Dimensions(display_width, display_height)