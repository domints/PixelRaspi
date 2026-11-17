from collections import namedtuple

from pixel import HwSerial, Pixel, WaveshareEthernet
from pixel.renderer import ColorMode, PixelRenderer

from flipdot.pixelmock import PixelMock

Dimensions: type[tuple[int, int]] = namedtuple('Dimensions', ['width', 'height'])


class UnknownDisplayError(ValueError):
    """The requested bus address was not probed at startup."""

pixel: Pixel | PixelMock | None = None
requested_ids: list[int] = []
displays: dict[int, Dimensions] = {}
renderers: dict[int, PixelRenderer] = {}
display_controllers: dict[int, str] = {}
default_id: int = -1
# Used only when a panel's GID / factory id does not say which controller it is.
controller: str = "8051"
controller_overrides: dict[int, str] = {}
encoding: str | None = None
color_mode: ColorMode = ColorMode.MONO


def _as_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def _optional_int(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in ("", "null", "none"):
        return None
    return int(value)


def _optional_str(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in ("", "null", "none"):
        return None
    return text


def _parse_color_mode(name: str | None) -> ColorMode:
    key = (name or "mono").strip().lower()
    mapping = {
        "mono": ColorMode.MONO,
        "gray4": ColorMode.GRAY4,
        "grey4": ColorMode.GRAY4,
        "rgb": ColorMode.RGB,
    }
    try:
        return mapping[key]
    except KeyError:
        raise ValueError(f"Unknown PIXEL_COLOR_MODE {name!r}; use mono, gray4, or rgb") from None


def normalize_controller(name: str) -> str:
    """Return ``8051`` or ``lpc1768``. Raises ``ValueError`` on an unknown name."""
    renderer = Pixel.make_renderer(name, 8, 8)
    return renderer.controller


def _parse_controller_overrides(value) -> dict[int, str]:
    if not value:
        return {}
    if not isinstance(value, dict):
        raise ValueError("PIXEL_CONTROLLERS must be an object of display id -> controller")
    return {int(display_id): normalize_controller(str(name)) for display_id, name in value.items()}


def detect_controller(gid: str, factory_id: str, fallback: str) -> str:
    """Pick a renderer family from what the panel reported.

    LPC1768 firmware identifies as ``XTD…`` and puts ``256`` in the third ``GID``
    field (``G96x36x256``). 8051 ``PIXEL-SIMS`` puts ``14`` there
    (``G112x16x14``, ``G84x16x14``). Anything else uses *fallback*.
    """
    if factory_id and "XTD" in factory_id.upper():
        return "lpc1768"
    body, _, _suffix = gid.partition("/")
    parts = body.split("x")
    third = parts[2] if len(parts) > 2 else ""
    if third == "256":
        return "lpc1768"
    if third in ("14", "0E", "0e"):
        return "8051"
    return fallback


def start_pixel(
    port: str | None = "/dev/serial0",
    pin=18,
    useMock: bool = False,
    display_ids: list[int] | None = None,
    *,
    eth_host: str | None = None,
    eth_port=None,
    baud=4800,
    controller_name: str | None = "8051",
    encoding_name: str | None = None,
    color_mode_name: str | None = "mono",
    controller_overrides_value=None,
    rts_toggle=False,
    rs485=False,
):
    global pixel, requested_ids, controller, controller_overrides, encoding, color_mode
    _reset_displays()
    requested_ids = list(display_ids) if display_ids else [0]
    controller = normalize_controller(_optional_str(controller_name) or "8051")
    controller_overrides = _parse_controller_overrides(controller_overrides_value)
    encoding = _optional_str(encoding_name)
    color_mode = _parse_color_mode(color_mode_name)

    de_pin = _optional_int(pin)
    tcp_port = _optional_int(eth_port)
    host = _optional_str(eth_host)
    serial_baud = _optional_int(baud) or 4800

    if _as_bool(useMock):
        pixel = PixelMock("G112x16x14/SOS1P02")
        reload_displays()
        return

    if host is not None:
        if tcp_port is None:
            raise ValueError("PIXEL_ETH_PORT is required when PIXEL_ETH_HOST is set")
        conn = WaveshareEthernet((host, tcp_port))
        where = f"Waveshare Ethernet serial server at {host}:{tcp_port}"
    else:
        serial_port = port or "/dev/serial0"
        conn = HwSerial(
            serial_port,
            de_pin=de_pin,
            baud=serial_baud,
            rts_toggle=_as_bool(rts_toggle),
            rs485=_as_bool(rs485),
        )
        where = f"serial port {serial_port}"

    pixel = Pixel(conn)
    if pixel.open():
        reload_displays()
    else:
        print(f"Could not connect to {where}")


def _reset_displays():
    global default_id
    default_id = -1
    displays.clear()
    renderers.clear()
    display_controllers.clear()


def reload_displays():
    global default_id
    _reset_displays()
    if pixel is None:
        return
    for id in requested_ids:
        try:
            gid = pixel.get_gid(id)
            body = gid.split('/')[0]
            dimensions = body.split('x')
            display_width = int(dimensions[0][1:])
            display_height = int(dimensions[1])
            try:
                factory_id = pixel.get_factory_identification(id)
            except Exception as factory_error:
                factory_id = ""
                print(f'Display {id} factory id unavailable ({factory_error}).')
            if id in controller_overrides:
                panel_controller = controller_overrides[id]
            else:
                panel_controller = detect_controller(gid, factory_id, controller)
            print(f'Display {id} ->  width: {display_width}, height: {display_height}, controller: {panel_controller}')
            if factory_id:
                print(factory_id)
            print()
            if default_id < 0:
                default_id = id
            displays[id] = Dimensions(display_width, display_height)
            display_controllers[id] = panel_controller
            renderers[id] = Pixel.make_renderer(
                panel_controller, display_width, display_height, color_mode=color_mode)
        except Exception as e:
            print(f'Display {id} cannot be connected to ({e}).')
            print()


def is_valid_id(id: int) -> bool:
    return id in displays


def validate_id(id: int) -> int:
    if is_valid_id(id):
        return id
    raise UnknownDisplayError("No such display id")


def resolve_id(display_id: int | None) -> int:
    if display_id is None:
        display_id = default_id
    return validate_id(display_id)


def get_dimensions(id: int) -> Dimensions:
    return displays[id]


def get_renderer(id: int) -> PixelRenderer:
    try:
        return renderers[id]
    except KeyError:
        raise UnknownDisplayError("No such display id") from None
