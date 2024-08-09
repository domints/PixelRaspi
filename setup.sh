#!/bin/sh

if [[ $EUID -ne 0 ]]; then
    echo "You must be root to do this." 1>&2
    exit 100
fi

chmod +x update.sh

cp flipdot.service /etc/systemd/system/flipdot.service
systemctl daemon-reload
systemctl enable flipdot
systemctl start flipdot
