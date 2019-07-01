#!/bin/bash

apt-get update
apt-get -y install python3-pip cron p7zip-full

pip3 install -r requirements.txt

export $(cat .env | xargs)

(crontab -l 2>/dev/null; echo "0 2 * * * /backuper/create_dump.sh") | crontab -
