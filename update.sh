#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "You must be root to do this." 1>&2
    exit 100
fi

systemctl stop flipdot
git pull
.venv/bin/pip install -r requirements.txt -U
systemctl start flipdot