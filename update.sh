#!/bin/sh

if [[ $EUID -ne 0 ]]; then
    echo "You must be root to do this." 1>&2
    exit 100
fi

systemctl stop flipdot
git pull
systemctl start flipdot