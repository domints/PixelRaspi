# PixelRaspi

API that will be able to control Pixel Bydgoszcz display using RS485 on Raspi (we're using Pi Zero W).

First thing you need on raspi, to enable UART.
Run `sudo raspi-config`, select `Interface Options` -> `Serial` -> Disable login shell over serial, enable serial port hardware. On PiZeroW you need to add `dtoverlay=disable-bt` to `/boot/firmware/config.txt`.

It would be great if you cloned that repo to `/opt/PixelRaspi` (just `cd /opt && sudo git clone https://github.com/domints/PixelRaspi.git`), then executed `sudo setup.sh`, it should set permissions, create systemd unit and start it.

To update execute `sudo update.sh`, it'll stop the service, pull latest repo code and restart the service.

Just make sure your filesystem is writable (disable overlay fs when updating).

This service talks to the display through [pixel-flipdot](https://github.com/domints/PixelFlipDot) 0.1 (the `pixel.renderer` engine and the `HwSerial` / `WaveshareEthernet` transports).

Images are sent with `Pixel.make_renderer(...).render_image(...)`. The 8051 flip-dot path defaults to `nibble_rle`. LPC1768 defaults to the renderer's mono `bitmap` encoding. Set `PIXEL_ENCODING` to override either one (`bitmap`, `nibble_rle`, …).

If you're using Waveshare CAN/RS485 hat, create folder `instance` and inside file `config.json` with following value:

    {
        "PIXEL_PIN": 4
    }

`PIXEL_PIN` is the RS-485 driver-enable GPIO (`HwSerial(de_pin=...)`). Leave it null for USB adapters that handle direction themselves. `PIXEL_BAUD` defaults to `4800`. Fast panels run at `19200`. The baud rate belongs to the whole RS-485 line, so every panel on one bus has to use the same value. `PIXEL_RTS_TOGGLE` and `PIXEL_RS485` turn on the matching `HwSerial` direction modes.

If you want to use it on PC, create folder `instance` and inside file `config.json` with following value, filling `PIXEL_PORT` with whatever identifies your serial port:

    {
        "PIXEL_PORT": "[port name]",
        "PIXEL_PIN": null
    }

For some reasons you might want to add `PIXEL_PORT` for raspberry too, if your port is not `/dev/serial0` (sometimes on Pi Zero W?).

Waveshare RS485-to-Ethernet serial servers use a TCP socket instead of a local UART. The baud rate is set on the Waveshare itself, and `PIXEL_BAUD` has no effect on that path. Set the bridge to `19200` for fast panels. `PIXEL_ETH_HOST` wins over `PIXEL_PORT` when it is set:

    {
        "PIXEL_ETH_HOST": "10.42.76.80",
        "PIXEL_ETH_PORT": 4196,
        "PIXEL_CONTROLLER": "lpc1768"
    }

Each address in `DISPLAY_IDS` is probed on its own. Width and height come from that panel's `GID` (`G96x36x256` is 96×36, `G112x16x14` is 112×16), and the renderer is built for that size. A 112×16 flip-dot and a 96×36 LPC can share the bus.

The controller family is chosen per address too. `XTD` in the factory id, or a `GID` third field of `256` (`G96x36x256`), selects `lpc1768`. A third field of `14` (`G112x16x14`, `G84x16x14`) selects `8051`. `PIXEL_CONTROLLER` is only the fallback when a panel matches neither (default `8051`). `PIXEL_COLOR_MODE` (`mono`, `gray4`, `rgb`) applies to every LPC renderer on the bus. `PIXEL_CONTROLLERS` overrides detection for specific decimal addresses:

    {
        "DISPLAY_IDS": [0, 11],
        "PIXEL_CONTROLLERS": {
            "0": "8051",
            "11": "lpc1768"
        }
    }

Addresses in `DISPLAY_IDS` and in request query parameter `id` are decimal. On the wire they are a single hex digit, so `11` is panel `B`. Requests without `id` go to the first panel that answered.

`/display/image` sends the uploaded picture to that panel's own renderer, so the image has to fit that panel. `/display/text` and `/display/complex` also allocate a canvas of that panel's size, but the text layout still draws at most two rows in the top 16 pixels.

`POST /actions/validators_block` is bus-wide. The clock job follows the first panel that answered, not a hardcoded address.

If you don't want to connect to hardware display, you can use mock device, which lets app work without display, create config file as above with contents:

    {
        "PIXEL_USE_MOCK": true
    }

## Docker compose for Dell Edge Gateway

Because Dell Edge Gateway comes with Ubuntu Core which is weird, I created Docker container with this code, and compose which lets you run it in Docker on this funny machine (Edge Gateway 3001 has hardware RS485 and is dirt cheap).

This compose exposes port `/dev/ttyXRUSB0` which is marked as IOIO2 on the device. Connect A (+) to pin 2, and B (-) to pin 1 (docs here: https://www.dell.com/support/manuals/pl-pl/dell-edge-gateway-3000-series/dell-edge_gateway-3001-install_manual/szczeg%C3%B3%C5%82owy-opis-definicji-styk%C3%B3w-portu-gpio?guid=guid-38545a5b-1b10-43ca-800b-7a696af28f26 ), they are counted from top-right, top to bottom then to left (looking at the device's port). 
You need to reconfigure port to use RS485 (`dcc.cctk --serial1=rs485` and `dcc.cctk --serial2=rs485`). Then you need to reboot. Make sure your CMOS battery is fine, otherwise it'll forget serial settings on power disconnect.

Provided compose runs this repo, as a translator of HTTP to pixel's proto, and Node-Red as coordinator. Example flow is provided in this repo, with "TDMA" kind of governor which dynamically changes displayed data.

## Additional resources

If you'd like to look for extra icons for your project, here are bunch of links. For licensing reasons I can't include them here, although I think they are fitting brilliantly onto flipdot display - just plop PNGs into the icons folder:

 * https://github.com/breqdev/weather-pixel-icons - awesome set of weather icons for your weather project. Just grab ordinary 16x16 icon set
