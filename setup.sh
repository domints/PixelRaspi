#!/bin/sh

if [[ $EUID -ne 0 ]]; then
    echo "You must be root to do this." 1>&2
    exit 100
fi

user_id=$(echo $UID)
group_id=$(id -g $UID)

chown -R $user_id:$group_id .
chmod +x update.sh

python -m venv .venv
.venv/bin/pip install -r requirements.txt

cp flipdot.service /etc/systemd/system/flipdot.service
systemctl daemon-reload
systemctl enable flipdot
systemctl start flipdot
