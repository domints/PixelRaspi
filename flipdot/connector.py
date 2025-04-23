from collections import namedtuple
from pixel import Pixel

from flipdot.pixelmock import PixelMock
Dimensions: type[tuple[int, int]] = namedtuple('Dimensions', ['width', 'height'])

pixel: Pixel = None

#display_width: int = 0
#display_height: int = 0
requested_ids: list[int] = []
displays: dict[int, Dimensions] = {}
default_id: int = -1

def start_pixel(port: str, pin: int | None = None, useMock: bool = False, display_ids: list[int] = [ 0 ]):
    global pixel
    global default_id
    global requested_ids
    requested_ids = display_ids
    #global display_width
    #global display_height
    if useMock:
        pixel = PixelMock("G112x16x14/SOS1P02")
    else:
        pixel = Pixel(port, pin)
        pixel.open()
    reload_displays()

def reload_displays():
    global requested_ids
    default_id = -1
    for id in requested_ids:
        try:
            gid = pixel.get_gid(id)
            parts = gid.split('/')
            dimensions = parts[0].split('x')
            display_width = int(dimensions[0][1:])
            display_height = int(dimensions[1])
            print(f'Display {id} ->  width: {display_width}, height: {display_height}')
            print(pixel.get_factory_identification(id))
            print()
            if default_id < 0:
                default_id = id
            displays[id] = Dimensions(display_width, display_height)
        except:
            if id in displays.keys():
                displays.pop(id)
            print(f'Display {id} cannot be connected to.')
            print()

def is_valid_id(id: int) -> bool:
    return id in displays.keys()

def validate_id(id: int) -> int:
    if is_valid_id(id):
        return id
    
    raise ValueError("No such ID defined")

def get_dimensions(id: int) -> Dimensions:
    return displays[id]