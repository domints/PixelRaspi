from pixel import Pixel

px: Pixel = None

def start_pixel(port: str, pin: int | None = None):
    global px
    px = Pixel(port, pin)
    px.open()