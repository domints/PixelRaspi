# PixelRaspi

API that will be able to control Pixel Bydgoszcz display using RS485 on Raspi (we're using Pi Zero W).

It would be great if you cloned that repo to `/opt/PixelRaspi` (just `cd /opt && sudo git clone https://github.com/domints/PixelRaspi.git`), then executed `sudo setup.sh`, it should set permissions, create systemd unit and start it.

To update execute `sudo update.sh`, it'll stop the service, pull latest repo code and restart the service.

Just make sure your filesystem is writable (disable overlay fs when updating).