# PixelRaspi

API that will be able to control Pixel Bydgoszcz display using RS485 on Raspi (we're using Pi Zero W).

First thing you need on raspi, to enable UART.
Run `sudo raspi-config`, select `Interface Options` -> `Serial` -> Disable login shell over serial, enable serial port hardware. On PiZeroW you need to add `dtoverlay=disable-bt` to `/boot/firmware/config.txt`.

It would be great if you cloned that repo to `/opt/PixelRaspi` (just `cd /opt && sudo git clone https://github.com/domints/PixelRaspi.git`), then executed `sudo setup.sh`, it should set permissions, create systemd unit and start it.

To update execute `sudo update.sh`, it'll stop the service, pull latest repo code and restart the service.

Just make sure your filesystem is writable (disable overlay fs when updating).

If you're using Waveshare CAN/RS485 hat, create folder `instance` and inside file `config.json` with following value:

    {
        "PIXEL_PIN": 4
    }

If you want to use it on PC, create folder `instance` and inside file `config.json` with following value, filling `PIXEL_PORT` with whatever identifies your serial port:

    {
        "PIXEL_PORT": "[port name]",
        "PIXEL_PIN": null
    }

For some reasons you might want to add `PIXEL_PORT` for raspberry too, if your port is not `/dev/serial0` (sometimes on Pi Zero W?).

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
