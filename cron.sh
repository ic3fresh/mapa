#!/bin/bash

PATH="/opt/mapa"
DEST="/var/www/mapa"

/usr/bin/python $PATH/getusers.py > $PATH/users.json && /bin/cp $PATH/users.json $DEST/users.json || echo "mapa: dane nie pobraly sie poprawnie"
