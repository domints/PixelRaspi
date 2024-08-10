from pixel import Pixel

px: Pixel = None
width: int = 0
height: int = 0

def start_pixel(port: str, pin: int | None = None):
    global px
    global width
    global height
    px = Pixel(port, pin)
    px.open()
    gid = px.get_gid(0)
    parts = gid.split('/')
    dimensions = parts[0].split('x')
    width = int(dimensions[0][1:])
    height = int(dimensions[1])